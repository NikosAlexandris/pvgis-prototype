from pvgisprototype.web_api.cache.redis import USE_REDIS_CACHE
from pvgisprototype.web_api.cache.caching import custom_cached
from pvgisprototype.log import logger

import math
from datetime import datetime
from typing import Annotated
from urllib.parse import quote

from fastapi.responses import ORJSONResponse, PlainTextResponse, Response
from pandas import DatetimeIndex

from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.api.irradiance.models import (
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.algorithms.huld.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    ShadingModel,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.power.broadband_multiple_surfaces import (
    calculate_photovoltaic_power_output_series_from_multiple_surfaces,
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
    ALBEDO_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    EFFICIENCY_FACTOR_DEFAULT,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    PEAK_POWER_DEFAULT,
    ECCENTRICITY_PHASE_OFFSET,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_OUTPUT_FILENAME,
    QUIET_FLAG_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    SOLAR_CONSTANT,
    STATISTICS_FLAG_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SYSTEM_EFFICIENCY_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
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
    fastapi_dependable_linke_turbidity_factor_series,
    fastapi_dependable_longitude,
    fastapi_dependable_quiet,
    fastapi_dependable_read_datasets,
    fastapi_dependable_shading_model,
    fastapi_dependable_solar_incidence_models,
    fastapi_dependable_solar_position_models,
    fastapi_dependable_surface_orientation_list,
    fastapi_dependable_surface_tilt_list,
    fastapi_dependable_timestamps,
    fastapi_dependable_timezone,
    fastapi_dependable_verbose,
)
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_albedo,
    fastapi_query_apply_reflectivity_factor,
    fastapi_query_csv,
    fastapi_query_eccentricity_correction_factor,
    fastapi_query_efficiency,
    fastapi_query_elevation,
    fastapi_query_end_time,
    fastapi_query_peak_power,
    fastapi_query_eccentricity_phase_offset,
    fastapi_query_periods,
    fastapi_query_photovoltaic_module_model,
    fastapi_query_power_model,
    fastapi_query_quick_response_code,
    fastapi_query_solar_constant,
    fastapi_query_solar_time_model,
    fastapi_query_start_time,
    fastapi_query_statistics,
    fastapi_query_system_efficiency,
    fastapi_query_temperature_model,
    fastapi_query_zero_negative_solar_incidence_angle,
)
from pvgisprototype.web_api.schemas import (
    AngleOutputUnit,
    Frequency,
    GroupBy,
    Timezone,
)


@custom_cached
async def get_photovoltaic_power_output_series_multi(
    _read_datasets: Annotated[
        dict, fastapi_dependable_read_datasets
    ],  # NOTE THIS ARGUMENT IS NOT INCLUDED IN SCHEMA AND USED ONLY FOR INTERNAL CALCULATIONS
    longitude: Annotated[float, fastapi_dependable_longitude] = 8.628,
    latitude: Annotated[float, fastapi_dependable_latitude] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[
        list[float], fastapi_dependable_surface_orientation_list
    ] = [float(SURFACE_ORIENTATION_DEFAULT)],
    surface_tilt: Annotated[list[float], fastapi_dependable_surface_tilt_list] = [
        float(SURFACE_TILT_DEFAULT)
    ],
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
    # spectral_factor_series: Annotated[
    #    SpectralFactorSeries, fastapi_dependable_spectral_factor_series
    # ] = None,
    shading_model: Annotated[
        ShadingModel, fastapi_dependable_shading_model
    ] = ShadingModel.pvis,
    linke_turbidity_factor_series: Annotated[
        float | LinkeTurbidityFactor, fastapi_dependable_linke_turbidity_factor_series
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    albedo: Annotated[float, fastapi_query_albedo] = ALBEDO_DEFAULT,
    apply_reflectivity_factor: Annotated[
        bool, fastapi_query_apply_reflectivity_factor
    ] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: Annotated[
        SolarPositionModel, fastapi_dependable_solar_position_models
    ] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[
        SolarIncidenceModel, fastapi_dependable_solar_incidence_models
    ] = SolarIncidenceModel.iqbal,
    zero_negative_solar_incidence_angle: Annotated[
        bool, fastapi_query_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: Annotated[
        SolarTimeModel, fastapi_query_solar_time_model
    ] = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: Annotated[float, fastapi_query_solar_constant] = SOLAR_CONSTANT,
    eccentricity_phase_offset: Annotated[
            float, fastapi_query_eccentricity_phase_offset
    ] = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: Annotated[
        float, fastapi_query_eccentricity_correction_factor
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model
    ] = PHOTOVOLTAIC_MODULE_DEFAULT,
    peak_power: Annotated[float, fastapi_query_peak_power] = PEAK_POWER_DEFAULT,
    system_efficiency: Annotated[
        float, fastapi_query_system_efficiency
    ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[
        PhotovoltaicModulePerformanceModel, fastapi_query_power_model
    ] = PhotovoltaicModulePerformanceModel.king,
    # radiation_cutoff_threshold: Annotated[float, fastapi_query_radiation_cutoff_threshold] = RADIATION_CUTOFF_THRESHHOLD,
    temperature_model: Annotated[
        ModuleTemperatureAlgorithm, fastapi_query_temperature_model
    ] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[
        float | None, fastapi_query_efficiency
    ] = EFFICIENCY_FACTOR_DEFAULT,
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
    """Calculate the total photovoltaic power/energy generated for a series of
    surface orientation and tilt angle pairs, optionally for various
    technologies, free-standing or building-integrated, at a specific location
    and a given period.

    # Features

    - Arbitrary time series supported by [Pandas' DatetimeIndex](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html)
    - Optional algorithms for solar timing, positioning and the estimation of the solar incidence angle
    - Optionally Disable the atmospheric refraction for solar positioning
    - Optional power-rating models on top of optional module temperature models (pending integration of alternatives)
    - Get from simple to detailed output in form of **JSON**, **CSV** and **Excel** (the latter **pending implementation**)
    - Share a **QR-Code** with a summary of the analysis
    - **Fingerprint** your analysis
    - Document your analysis including all **input metadata**

    ## **Important Notes**

    - The function expects pairs of surface orientation
      (`surface_orientation`) and tilt (`surface_tilt`) angles, that is the
      number of requested orientation angles should equal the number of
      requested tilt angles.

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

    - time series data limited to the period **2014** - **2024**.
    - solar irradiance from the [SARAH3 climate records](https://wui.cmsaf.eu/safira/action/viewDoiDetails?acronym=SARAH_V003)
    - temperature and wind speed estimations from [ERA5 Reanalysis](https://www.ecmwf.int/en/forecasts/dataset/ecmwf-reanalysis-v5) collection
    - spectral effect factor time series (Huld, 2011) _for the reference year 2013_

    """
    logger.info(f"🔧 Endpoint starting - USE_REDIS_CACHE: {USE_REDIS_CACHE}")

    photovoltaic_power_output_series = calculate_photovoltaic_power_output_series_from_multiple_surfaces(
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
        linke_turbidity_factor_series=linke_turbidity_factor_series,  # LinkeTurbidityFactor = LinkeTurbidityFactor(value = LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        albedo=albedo,
        apply_reflectivity_factor=apply_reflectivity_factor,
        solar_position_model=solar_position_model,
        solar_incidence_model=solar_incidence_model,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        solar_time_model=solar_time_model,
        solar_constant=solar_constant,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        angle_output_units=angle_output_units,
        photovoltaic_module=photovoltaic_module,
        # peak_power=peak_power,
        system_efficiency=system_efficiency,
        power_model=power_model,
        # radiation_cutoff_threshold=radiation_cutoff_threshold,
        temperature_model=temperature_model,
        efficiency=efficiency,
        verbose=verbose,
        # log=verbose,
        fingerprint=True,
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

        return response

    response: dict = {}  # type: ignore
    headers = {
        "Content-Disposition": f'attachment; filename="{PHOTOVOLTAIC_POWER_OUTPUT_FILENAME}.json"'
    }

    if fingerprint:
        response[FINGERPRINT_COLUMN_NAME] = photovoltaic_power_output_series.components[  # type: ignore
            FINGERPRINT_COLUMN_NAME
        ]

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
            return Response(content=image_bytes, media_type="image/png")

    if statistics:
        from numpy import atleast_1d, ndarray

        from pvgisprototype.api.statistics.xarray import calculate_series_statistics

        series_statistics = calculate_series_statistics(
            data_array=photovoltaic_power_output_series.series,
            timestamps=timestamps,
            groupby=groupby,  # type: ignore[arg-type]
        )
        converted_series_statistics = {
            key: atleast_1d(value) if isinstance(value, ndarray) else value
            for key, value in series_statistics.items()
        }  # NOTE Important since calculate_series_statistics returns scalars and ORJSON cannot serielise them
        response["Statistics"] = converted_series_statistics  # type: ignore

    if not quiet:
        if verbose > 0:
            response = photovoltaic_power_output_series.components
        else:
            response = {
                PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series.series,  # type: ignore
            }

    return ORJSONResponse(response, headers=headers, media_type="application/json")
