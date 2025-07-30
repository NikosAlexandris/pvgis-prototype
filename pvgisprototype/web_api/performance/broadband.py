from typing import Annotated
from urllib.parse import quote

from fastapi import Request
from fastapi.responses import ORJSONResponse, PlainTextResponse, Response
from pandas import DatetimeIndex

from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import ShadingModel
from pvgisprototype.api.performance.report import summarise_photovoltaic_performance
from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.quick_response_code import (
    QuickResponseCode,
    generate_quick_response_code,
)
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMode
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.constants import (
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    METADATA_FLAG_DEFAULT,
    PEAK_POWER_DEFAULT,
    PHOTOVOLTAIC_PERFORMANCE_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_OUTPUT_FILENAME,
    ROUNDING_PLACES_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SYSTEM_EFFICIENCY_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    STATISTICS_FLAG_DEFAULT,
)
from pvgisprototype.web_api.dependencies import (
    fastapi_dependable_angle_output_units,
    fastapi_dependable_common_datasets,
    fastapi_dependable_convert_timestamps,
    fastapi_dependable_convert_timezone,
    fastapi_dependable_end_time,
    fastapi_dependable_fingerprint,
    fastapi_dependable_frequency,
    fastapi_dependable_latitude,
    fastapi_dependable_longitude,
    fastapi_dependable_quiet_for_performance_analysis,
    fastapi_dependable_read_datasets,
    fastapi_dependable_start_time,
    fastapi_dependable_surface_orientation,
    fastapi_dependable_surface_tilt,
    fastapi_dependable_timestamps,
    fastapi_dependable_timezone,
    fastapi_dependable_verbose_for_performance_analysis,
    fastapi_dependable_shading_model,
    fastapi_dependable_groupby,
    fastapi_dependable_optimise_surface_position,
)
from pvgisprototype.web_api.fastapi_parameters import (
    fastapi_query_analysis,
    fastapi_query_csv,
    fastapi_query_elevation,
    fastapi_query_end_time,
    fastapi_query_index,
    fastapi_query_peak_power,
    fastapi_query_periods,
    fastapi_query_photovoltaic_module_model,
    fastapi_query_power_model,
    fastapi_query_quick_response_code,
    fastapi_query_start_time,
    fastapi_query_system_efficiency,
    fastapi_query_statistics,
)
from pvgisprototype.web_api.schemas import (
    AnalysisLevel,
    AngleOutputUnit,
    Frequency,
    Timezone,
    GroupBy,
)


def get_metadata(request: Request):
    return {"Input query parameters": dict(request.query_params)}
    # return JSONResponse()


async def get_photovoltaic_performance_analysis(
    request: Request,
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
    start_time: Annotated[
        str | None, fastapi_query_start_time
    ] = "2014-01-01",  # Used by fastapi_query_start_time
    periods: Annotated[
        int | None, fastapi_query_periods
    ] = None,  # Used by fastapi_query_periods
    frequency: Annotated[Frequency, fastapi_dependable_frequency] = Frequency.Hourly,
    end_time: Annotated[
        str | None, fastapi_query_end_time
    ] = "2014-12-01",  # Used by fastapi_query_end_time
    timestamps: Annotated[DatetimeIndex | None, fastapi_dependable_timestamps] = None,
    timezone: Annotated[Timezone, fastapi_dependable_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
    shading_model: Annotated[
        ShadingModel, fastapi_dependable_shading_model
    ] = ShadingModel.pvis,
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model
    ] = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    system_efficiency: Annotated[
        float, fastapi_query_system_efficiency
    ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[
        PhotovoltaicModulePerformanceModel, fastapi_query_power_model
    ] = PhotovoltaicModulePerformanceModel.king,
    peak_power: Annotated[float, fastapi_query_peak_power] = PEAK_POWER_DEFAULT,
    statistics: Annotated[bool, fastapi_query_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[GroupBy, fastapi_dependable_groupby] = GroupBy.NoneValue,
    analysis: Annotated[AnalysisLevel, fastapi_query_analysis] = AnalysisLevel.Simple,
    csv: Annotated[str | None, fastapi_query_csv] = None,
    verbose: Annotated[
        int, fastapi_dependable_verbose_for_performance_analysis
    ] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, fastapi_query_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[
        bool, fastapi_dependable_quiet_for_performance_analysis
    ] = True,  # Keep me hardcoded !
    fingerprint: Annotated[
        bool, fastapi_dependable_fingerprint
    ] = FINGERPRINT_FLAG_DEFAULT,
    # metadata: Annotated[bool, typer_option_command_metadata] = METADATA_FLAG_DEFAULT,
    metadata: bool = METADATA_FLAG_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
    optimise_surface_position: Annotated[
        SurfacePositionOptimizerMode, fastapi_dependable_optimise_surface_position
    ] = SurfacePositionOptimizerMode.NoneValue,
    timezone_for_calculations: Annotated[
        Timezone, fastapi_dependable_convert_timezone
    ] = Timezone.UTC,  # type: ignore # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
    user_requested_timestamps: Annotated[
        DatetimeIndex | None, fastapi_dependable_convert_timestamps
    ] = None,  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
) -> ORJSONResponse:
    """Analyse the photovoltaic performance for a solar surface, various
    technologies, free-standing or building-integrated, at a specific location
    and a given period.

    # Features

    - A symbol nomenclature for easy identification of quantities, units, and more -- see [Symbols](https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/cli/symbols/)
    - Arbitrary time series supported by [Pandas' DatetimeIndex](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html)
    - Valid time zone identifiers from [the IANA Time Zone Database](https://www.iana.org/time-zones)
    - Surface position optimisation supported by [SciPy](https://docs.scipy.org/doc/scipy/reference/optimize.html) (**pending integration**)
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
    if optimise_surface_position:
        surface_orientation = optimise_surface_position["Surface Orientation"].value  # type: ignore
        surface_tilt = optimise_surface_position["Surface Tilt"].value  # type: ignore

    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
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
        photovoltaic_module=photovoltaic_module,
        angle_output_units=angle_output_units,
        system_efficiency=system_efficiency,
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
            dictionary=photovoltaic_power_output_series.components,
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

        return response  # type: ignore

    response: dict = {}  # type: ignore

    headers = {
        "Content-Disposition": f'attachment; filename="{PHOTOVOLTAIC_POWER_OUTPUT_FILENAME}.json"'
    }

    if fingerprint:
        response[FINGERPRINT_COLUMN_NAME] = photovoltaic_power_output_series.components[  # type: ignore
            FINGERPRINT_COLUMN_NAME
        ]

    if not quiet:
        if verbose > 0:
            response = photovoltaic_power_output_series.components
        else:
            response = {
                PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series.value,
            }  # type: ignore

    if analysis.value != AnalysisLevel.NoneValue:
        photovoltaic_performance_report = summarise_photovoltaic_performance(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_orientation=True if surface_orientation else False,
            surface_tilt=True if surface_tilt else False,
            dictionary=photovoltaic_power_output_series.components,
            timestamps=user_requested_timestamps,
            angle_output_units=angle_output_units,
            frequency=frequency,
            analysis=analysis,
        )
        response[PHOTOVOLTAIC_PERFORMANCE_COLUMN_NAME] = photovoltaic_performance_report  # type: ignore

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

    if metadata:
        response["Metadata"] = get_metadata(request=request)  # type: ignore

    if quick_response_code.value != QuickResponseCode.NoneValue:
        quick_response = generate_quick_response_code(
            dictionary=photovoltaic_power_output_series.components,
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
            return Response(content=image_bytes, media_type="image/png")  # type: ignore
        else:
            return ORJSONResponse({"message": "No QR code generated."})

    return ORJSONResponse(response, headers=headers, media_type="application/json")
