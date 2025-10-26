from pvgisprototype.cli.print.fingerprint import retrieve_fingerprint
from pvgisprototype.core.hashing import convert_numpy_to_json_serializable
from pvgisprototype.web_api.cache.caching import custom_cached
from pvgisprototype.log import logger

from datetime import datetime
from typing import Annotated
from urllib.parse import quote

from fastapi.responses import ORJSONResponse, PlainTextResponse, Response
from pandas import DatetimeIndex

from pvgisprototype.algorithms.huld.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import (
    ShadingModel,
)
from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)
from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.quick_response_code import (
    QuickResponseCode,
    generate_quick_response_code,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.constants import (
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    PEAK_POWER_DEFAULT,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_OUTPUT_FILENAME,
    QUIET_FLAG_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    STATISTICS_FLAG_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SYSTEM_EFFICIENCY_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    PHOTOVOLTAIC_MODULE_DEFAULT,
)
from pvgisprototype.web_api.dependency.dependable import (
    fastapi_dependable_angle_output_units,
    fastapi_dependable_convert_timestamps,
    fastapi_dependable_convert_timezone,
    fastapi_dependable_fingerprint,
    fastapi_dependable_frequency,
    fastapi_dependable_groupby,
    fastapi_dependable_latitude,
    fastapi_dependable_longitude,
    fastapi_dependable_quiet,
    fastapi_dependable_read_datasets,
    fastapi_dependable_shading_model,
    fastapi_dependable_surface_orientation,
    fastapi_dependable_surface_tilt,
    fastapi_dependable_timestamps,
    fastapi_dependable_timezone,
    fastapi_dependable_verbose,
)
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_csv,
    fastapi_query_elevation,
    fastapi_query_end_time,
    fastapi_query_peak_power,
    fastapi_query_periods,
    fastapi_query_photovoltaic_module_model,
    fastapi_query_power_model,
    fastapi_query_quick_response_code,
    fastapi_query_start_time,
    fastapi_query_statistics,
    fastapi_query_system_efficiency,
)
from pvgisprototype.web_api.schemas import (
    AngleOutputUnit,
    Frequency,
    GroupBy,
    Timezone,
)


@custom_cached
async def get_photovoltaic_power_series(
    _read_datasets: Annotated[
        dict, fastapi_dependable_read_datasets
    ],  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[
        float, fastapi_dependable_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[
        float, fastapi_dependable_surface_tilt
    ] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[str | None, fastapi_dependable_timestamps] = None,
    start_time: Annotated[
        datetime | None, fastapi_query_start_time
    ] = datetime.fromisoformat("2014-01-01 00:00:00"),
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hourly,
    end_time: Annotated[
        datetime | None, fastapi_query_end_time
    ] = datetime.fromisoformat("2014-12-31 23:59:59"),
    timezone: Annotated[Timezone, fastapi_dependable_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
    shading_model: Annotated[
        ShadingModel, fastapi_dependable_shading_model
    ] = ShadingModel.pvis,
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model
    ] = PHOTOVOLTAIC_MODULE_DEFAULT,
    system_efficiency: Annotated[
        float, fastapi_query_system_efficiency
    ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[
        PhotovoltaicModulePerformanceModel, fastapi_query_power_model
    ] = PhotovoltaicModulePerformanceModel.king,
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    peak_power: Annotated[float, fastapi_query_peak_power] = PEAK_POWER_DEFAULT,
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[GroupBy, fastapi_dependable_groupby] = GroupBy.NoneValue,
    csv: Annotated[str | None, fastapi_query_csv] = None,
    verbose: Annotated[int, fastapi_dependable_verbose] = VERBOSE_LEVEL_DEFAULT,
    quiet: Annotated[bool, fastapi_dependable_quiet] = QUIET_FLAG_DEFAULT,
    fingerprint: Annotated[
        bool, fastapi_dependable_fingerprint
    ] = FINGERPRINT_FLAG_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
    timezone_for_calculations: Annotated[
        Timezone, fastapi_dependable_convert_timezone
    ] = Timezone.UTC,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
    user_requested_timestamps: Annotated[
        DatetimeIndex | None, fastapi_dependable_convert_timestamps
    ] = None,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
):
    """
    **DEMO**: Estimate the photovoltaic power output for a solar surface.

    Estimate the photovoltaic power for a solar surface over a time series or an arbitrarily aggregated energy production of a PV system connected to the electricity
    grid (without battery storage) based on broadband solar irradiance, ambient temperature and wind speed.

    # Features

    - A symbol nomenclature for easy identification of quantities, units, and more -- see [Symbols](https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/cli/symbols/)
    - Arbitrary time series supported by [Pandas' DatetimeIndex](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html)
    - Valid time zone identifiers from [the IANA Time Zone Database](https://www.iana.org/time-zones)
    - Get from simple to detailed output in form of **JSON**, **CSV** and **Excel** (the latter **pending implementation**)
    - Share a **QR-Code** with a summary of the analysis
    - **Fingerprint** your analysis
    - Document your analysis including all **input metadata**

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

    ## Need more control ?

    In the `/power/broadband` endpoint you may find :

    - Optional algorithms for solar timing, positioning and the estimation of the solar incidence angle
    - Disable atmospheric refraction for solar positioning
    - Simpler power-rating model as well as module temperature model
    - and more

    # Algorithms & Models

    - Solar radiation model by Hofierka, 2002
    - Photovoltaic efficiency coefficients by ESTI, C2, JRC, European Commission
    - Solar positioning based on NOAA's solar geometry equations
    - Reflectivity effect as a function of the solar incidence angle by Martin and Ruiz, 2005
    - Spectal mismatch effect by Huld, 2011
    - Overall system efficiency pre-set to 0.86, in other words 14% of loss for material degradation, aging, etc.

    # Input data

    This function consumes internally :

    - time series data limited to the period **2014** - **2024**.
    - solar irradiance from the [SARAH3 climate records](https://wui.cmsaf.eu/safira/action/viewDoiDetails?acronym=SARAH_V003)
    - temperature and wind speed estimations from [ERA5 Reanalysis](https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5) collection
    - spectral effect factor time series (Huld, 2011) _for the reference year 2013_

    """
    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone_for_calculations,
        global_horizontal_irradiance=_read_datasets[
            "global_horizontal_irradiance_series"
        ],
        direct_horizontal_irradiance=_read_datasets[
            "direct_horizontal_irradiance_series"
        ],
        temperature_series=_read_datasets["temperature_series"],
        wind_speed_series=_read_datasets["wind_speed_series"],
        spectral_factor_series=_read_datasets["spectral_factor_series"],
        horizon_profile=_read_datasets["horizon_profile"],
        shading_model=shading_model,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        photovoltaic_module=photovoltaic_module,
        system_efficiency=system_efficiency,
        # angle_output_units=angle_output_units,
        power_model=power_model,
        peak_power=peak_power,
        verbose=verbose,
        fingerprint=fingerprint,
    )

    # -------------------------------------------------------------- Important
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    # ------------------------------------------------------------------------

    if csv:
        from pvgisprototype.web_api.utilities import generate_photovoltaic_output_csv

        in_memory_csv = generate_photovoltaic_output_csv(
            dictionary=photovoltaic_power_output_series.output,
            latitude=latitude,
            longitude=longitude,
            timestamps=user_requested_timestamps,
            timezone=timezone,  # type: ignore
        )

        # Based on https://github.com/fastapi/fastapi/discussions/9049 since file is already in memory is faster to return it as PlainTextResponse
        response = PlainTextResponse(
            content=in_memory_csv,
            headers={"Content-Disposition": f"attachment; filename={quote(csv)}"},
            media_type="text/csv",
        )

        return response

    response: dict = {}  # type: ignore
    headers = {
        "Content-Disposition": f'attachment; filename="{PHOTOVOLTAIC_POWER_OUTPUT_FILENAME}.json"'
    }

    if fingerprint:
        response[FINGERPRINT_COLUMN_NAME] = retrieve_fingerprint(photovoltaic_power_output_series.output)

    if quick_response_code.value != QuickResponseCode.NoneValue:
        quick_response = generate_quick_response_code(
            dictionary=photovoltaic_power_output_series.output,
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

    if statistics:
        from numpy import atleast_1d, ndarray

        from pvgisprototype.api.statistics.xarray import calculate_series_statistics

        series_statistics = calculate_series_statistics(
            data_array=photovoltaic_power_output_series.value,
            timestamps=user_requested_timestamps,
            groupby=groupby,  # type: ignore[arg-type]
        )
        converted_series_statistics = {
            key: atleast_1d(value) if isinstance(value, ndarray) else value
            for key, value in series_statistics.items()
        }  # NOTE Important since calculate_series_statistics returns scalars and ORJSON cannot serielise them
        response["Statistics"] = converted_series_statistics  # type: ignore

    if not quiet:
        if verbose > 0:
            response = photovoltaic_power_output_series.output
        else:
            response = {
                PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series.value,  # type: ignore
            }

    # Convert numpy objects to JSON-serializable types
    json_safe_response = convert_numpy_to_json_serializable(response)

    return ORJSONResponse(json_safe_response, headers=headers, media_type="application/json")
