from typing import Annotated
from urllib.parse import quote

from fastapi import Depends
from fastapi.responses import ORJSONResponse
from pandas import DatetimeIndex

from pvgisprototype.api.quick_response_code import QuickResponseCode, generate_quick_response_code
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerModeWithoutNone,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME, FINGERPRINT_FLAG_DEFAULT, ROUNDING_PLACES_DEFAULT
from pvgisprototype.web_api.dependencies import (
    fastapi_dependable_angle_output_units,
    fastapi_dependable_fingerprint,
    fastapi_dependable_convert_timestamps,
    process_optimise_surface_position,
)
from pvgisprototype.web_api.fastapi_parameters import (
    fastapi_query_csv,
    fastapi_query_optimise_surface_position,
    fastapi_query_quick_response_code,
)
from pvgisprototype.web_api.schemas import AngleOutputUnit


async def get_optimised_surface_position(
    surface_position_optimiser_mode: Annotated[
        SurfacePositionOptimizerModeWithoutNone, fastapi_query_optimise_surface_position
    ],
    optimal_surface_position: Annotated[
        dict, Depends(process_optimise_surface_position)
    ],
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    csv: Annotated[str | None, fastapi_query_csv] = None,
    fingerprint: Annotated[
        bool, fastapi_dependable_fingerprint
    ] = FINGERPRINT_FLAG_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
    user_requested_timestamps: Annotated[
        DatetimeIndex | None, fastapi_dependable_convert_timestamps
    ] = None,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
):
    """Estimate the optimal positioning of a solar surface (Orientation, Tilt or Orientation & Tilt), optionally for various technologies, at a specific location and a period in time.

    <span style="color:red"> <ins>**This Application Is a Feasibility Study**</ins></span>
    **limited to** longitudes ranging in [`7.5`, `10`] and latitudes in [`45`, `47.5`].

    # Features

    - A symbol nomenclature for easy identification of quantities, units, and more -- see [Symbols](https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/cli/symbols/)
    - Arbitrary time series supported by [Pandas' DatetimeIndex](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html)
    - Valid time zone identifiers from [the IANA Time Zone Database](https://www.iana.org/time-zones)
    - Surface position optimisation supported by [SciPy](https://docs.scipy.org/doc/scipy/reference/optimize.html)
    - Get from simple to detailed output in form of **JSON**, **CSV** and **Excel** (the latter **pending implementation**)

    ## **Important Notes**

    - The default time, if not given, regardless of the `frequency` is
      `00:00:00`. It is then expected to get `0` incoming solar irradiance and
      subsequently photovoltaic power/energy output.

    - Of the four parameters `start_time`, `end_time`, `periods`, and
      `frequency`, exactly three must be specified. If `frequency` is omitted,
      the resulting timestamps (a Pandas `DatetimeIndex` object)
      will have `periods` linearly spaced elements between `start_time` and
      `end_time` (closed on both sides). Learn more about frequency strings at
      [Offset aliases](https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases).

    # Algorithms & Models

    - Solar radiation model by Hofierka, 2002
    - Photovoltaic efficiency coefficients by ESTI, C2, JRC, European Commission
    - Solar positioning based on NOAA's solar geometry equations
    - Reflectivity effect as a function of the solar incidence angle by Martin and Ruiz, 2005
    - Spectal mismatch effect by Huld, 2011
    - Overall system efficiency pre-set to 0.86, in other words 14% of loss for material degradation, aging, etc.

    # Input data

    This function consumes internally :

    - time series data limited to the period **2005** - **2023**.
    - solar irradiance from the [SARAH3 climate records](https://wui.cmsaf.eu/safira/action/viewDoiDetails?acronym=SARAH_V003)
    - temperature and wind speed estimations from [ERA5 Reanalysis](https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5) collection
    - spectral effect factor time series (Huld, 2011) _for the reference year 2013_
    """
    if csv:
        from fastapi.responses import StreamingResponse

        csv_content = ",".join(["Surface Orientation", "Surface Tilt"]) + "\n"
        csv_content += f"{convert_float_to_degrees_if_requested(optimal_surface_position['surface_orientation'].value, angle_output_units)},{convert_float_to_degrees_if_requested(optimal_surface_position['surface_tilt'].value, angle_output_units)}"
        response_csv = StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={quote(csv)}"},
        )

        return response_csv

    response: dict = {}
    headers = {
        "Content-Disposition": 'attachment; filename="pvgis_optimal_solar_surface_position.json"'
    }

    if fingerprint:
        response[FINGERPRINT_COLUMN_NAME] = optimal_surface_position[  # type: ignore
            FINGERPRINT_COLUMN_NAME
        ]

    if quick_response_code.value != QuickResponseCode.NoneValue:
        quick_response = generate_quick_response_code(
            dictionary=optimal_surface_position,
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_orientation=True,
            surface_tilt=True,
            timestamps=user_requested_timestamps,
            rounding_places=ROUNDING_PLACES_DEFAULT,
            output_type=quick_response_code,
        )

        if quick_response_code.value == QuickResponseCode.Base64:
            response["QR"] = f"data:image/png;base64,{quick_response}"  # type: ignore
        elif quick_response_code.value == QuickResponseCode.Image:
            from io import BytesIO

            buffer = BytesIO()
            image = quick_response.make_image()  # type: ignore
            image.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            return Response(content=image_bytes, media_type="image/png")

    response["Optimal Surface Position"] = {
        "Optimal surface orientation": convert_float_to_degrees_if_requested(
            optimal_surface_position["surface_orientation"].value, angle_output_units
        ),
        "Optimal surface tilt": convert_float_to_degrees_if_requested(
            optimal_surface_position["surface_tilt"].value, angle_output_units
        ),
    }

    return ORJSONResponse(response, headers=headers, media_type="application/json")
