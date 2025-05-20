import asyncio
import math
from pathlib import Path
from typing import Annotated, Dict, List, Optional, TypeVar
from zoneinfo import ZoneInfo

import numpy as np
from fastapi import Depends, HTTPException
from numpy import radians
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray

from pvgisprototype import (
    Latitude,
    LinkeTurbidityFactor,
    Longitude,
    SpectralFactorSeries,
    SurfaceOrientation,
    SurfaceTilt,
    TemperatureSeries,
    WindSpeedSeries,
)
from pvgisprototype.algorithms.tmy.models import TMYStatisticModel
from pvgisprototype.algorithms.tmy.weighting_scheme_model import MeteorologicalVariable
from pvgisprototype.api.datetime.datetimeindex import generate_timestamps
from pvgisprototype.api.datetime.timezone import generate_a_timezone, parse_timezone
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.position.models import (
    SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    ShadingModel,
    SolarIncidenceModel,
    SolarPositionModel,
)
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.api.series.direct_horizontal_irradiance import (
    get_direct_horizontal_irradiance_series,
)
from pvgisprototype.api.series.global_horizontal_irradiance import (
    get_global_horizontal_irradiance_series,
)
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.api.series.spectral_factor import get_spectral_factor_series
from pvgisprototype.api.series.temperature import get_temperature_series
from pvgisprototype.api.series.wind_speed import get_wind_speed_series
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.api.surface.positioning import optimise_surface_position
from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.cli.typer.shading import infer_horizon_azimuth_in_radians
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEGREES,
    FINGERPRINT_FLAG_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    NUMBER_OF_ITERATIONS_DEFAULT,
    NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    QUIET_FLAG_DEFAULT,
    RADIANS,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SPECTRAL_FACTOR_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_ORIENTATION_MAXIMUM,
    SURFACE_ORIENTATION_MINIMUM,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_MAXIMUM,
    SURFACE_TILT_MINIMUM,
    SYMBOL_UNIT_TEMPERATURE,
    SYMBOL_UNIT_WIND_SPEED,
    TEMPERATURE_DEFAULT,
    TIMEZONE_UTC,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    WIND_SPEED_DEFAULT,
)
from pvgisprototype.web_api.fastapi_parameters import (
    fastapi_query_analysis,
    fastapi_query_angle_output_units,
    fastapi_query_convert_timestamps,
    fastapi_query_csv,
    fastapi_query_direct_horizontal_irradiance,
    fastapi_query_elevation,
    fastapi_query_end_time,
    fastapi_query_fingerprint,
    fastapi_query_frequency,
    fastapi_query_global_horizontal_irradiance,
    fastapi_query_groupby,
    fastapi_query_horizon_profile,
    fastapi_query_horizon_profile_series,
    fastapi_query_in_memory,
    fastapi_query_iterations,
    fastapi_query_latitude,
    fastapi_query_latitude_in_degrees,
    fastapi_query_linke_turbidity_factor_series,
    fastapi_query_longitude,
    fastapi_query_longitude_in_degrees,
    fastapi_query_mask_and_scale,
    fastapi_query_meteorological_variable,
    fastapi_query_neighbor_lookup,
    fastapi_query_number_of_samping_points,
    fastapi_query_periods,
    fastapi_query_photovoltaic_module_model,
    fastapi_query_quick_response_code,
    fastapi_query_quiet,
    fastapi_query_refracted_solar_zenith,
    fastapi_query_sampling_method_shgo,
    fastapi_query_shading_model,
    fastapi_query_solar_incidence_model,
    fastapi_query_solar_position_model,
    fastapi_query_solar_position_models,
    fastapi_query_spectral_effect_series,
    fastapi_query_start_time,
    fastapi_query_surface_orientation,
    fastapi_query_surface_orientation_list,
    fastapi_query_surface_position_optimisation_method,
    fastapi_query_surface_position_optimisation_mode,
    fastapi_query_surface_tilt,
    fastapi_query_surface_tilt_list,
    fastapi_query_temperature_series,
    fastapi_query_timestamps,
    fastapi_query_timezone,
    fastapi_query_timezone_to_be_converted,
    fastapi_query_tmy_statistic_model,
    fastapi_query_tolerance,
    fastapi_query_use_timestamps_from_data,
    fastapi_query_verbose,
    fastapi_query_wind_speed_series,
)
from pvgisprototype.web_api.schemas import (
    AnalysisLevel,
    AngleOutputUnit,
    Frequency,
    GroupBy,
    Timezone,
)


async def _provide_common_datasets(
    global_horizontal_irradiance: Annotated[
        str, fastapi_query_global_horizontal_irradiance
    ] = "sarah2_sis_over_esti_jrc.nc",
    direct_horizontal_irradiance: Annotated[
        str, fastapi_query_direct_horizontal_irradiance
    ] = "sarah2_sid_over_esti_jrc.nc",
    temperature_series: Annotated[
        str, fastapi_query_temperature_series
    ] = "era5_t2m_over_esti_jrc.nc",
    wind_speed_series: Annotated[
        str, fastapi_query_wind_speed_series
    ] = "era5_ws2m_over_esti_jrc.nc",
    spectral_factor_series: Annotated[
        str, fastapi_query_spectral_effect_series
    ] = "spectral_effect_cSi_2013_over_esti_jrc.nc",
    horizon_profile_series: Annotated[
        str, fastapi_query_horizon_profile_series
    ] = "horizon_profile_12_076.zarr",
):
    """This is a helper function for providing the SIS, SID, temperature, wind speed, spectral effect data.
    This method is a deprecated temporary solution and will be replaced in the future.
    """

    global_horizontal_irradiance = "/var/www/data/sarah3_sis_12_076.nc"
    direct_horizontal_irradiance = "/var/www/data/sarah3_sid_12_076.nc"
    temperature_series = "/var/www/data/era5_t2m_12_076.nc"
    wind_speed_series = "/var/www/data/era5_ws2m_12_076.nc"
    spectral_factor_series = "/var/www/data/spectral_effect_cSi_12_076.nc"
    horizon_profile_series = "/var/www/data/horizon_12_076.zarr"

    return {
        "global_horizontal_irradiance_series": Path(global_horizontal_irradiance),
        "direct_horizontal_irradiance_series": Path(direct_horizontal_irradiance),
        "temperature_series": Path(temperature_series),
        "wind_speed_series": Path(wind_speed_series),
        "spectral_factor_series": Path(spectral_factor_series),
        "horizon_profile_series": Path(horizon_profile_series),
    }


async def process_longitude(
    longitude: Annotated[float, fastapi_query_longitude] = 8.628,
) -> Longitude:
    # return Longitude(value = convert_to_radians_fastapi(longitude), unit = RADIANS) # FIXME Revert to this when pydantic objects will be created
    return convert_to_radians_fastapi(longitude)


async def process_latitude(
    latitude: Annotated[float, fastapi_query_latitude] = 45.812,
) -> Latitude:
    # return Latitude(value = convert_to_radians_fastapi(latitude), unit = RADIANS) # FIXME Revert to this when pydantic objects will be created
    return convert_to_radians_fastapi(latitude)


async def process_surface_orientation(
    surface_orientation: Annotated[
        float, fastapi_query_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
) -> SurfaceOrientation:
    # return SurfaceOrientation(value = convert_to_radians_fastapi(surface_orientation), unit = RADIANS) # FIXME Revert to this when pydantic objects will be created
    return convert_to_radians_fastapi(surface_orientation)


async def process_surface_tilt(
    surface_tilt: Annotated[float, fastapi_query_surface_tilt] = SURFACE_TILT_DEFAULT,
) -> SurfaceTilt:
    # return SurfaceTilt(value = convert_to_radians_fastapi(surface_tilt), unit = RADIANS) # FIXME Revert to this when pydantic objects will be created
    return convert_to_radians_fastapi(surface_tilt)


def process_timezone(
    timezone: Annotated[Timezone, fastapi_query_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
) -> ZoneInfo:
    timezone = parse_timezone(timezone.value)  # type: ignore[assignment]
    return generate_a_timezone(timezone)  # type: ignore


async def process_timezone_to_be_converted(
    timezone_for_calculations: Annotated[Timezone, fastapi_query_timezone_to_be_converted] = Timezone.UTC,  # type: ignore[attr-defined]
) -> ZoneInfo:
    timezone_for_calculations = parse_timezone(timezone_for_calculations.value)  # type: ignore[assignment]
    return generate_a_timezone(timezone_for_calculations)  # type: ignore


TimeUnit = TypeVar("TimeUnit", GroupBy, Frequency)

time_groupings: Dict[str, str | None] = {
    "Yearly": "YE",
    "Seasonal": "S",
    "Monthly": "ME",
    "Weekly": "W",
    "Daily": "D",
    "Hourly": "h",
    "Minutely": "min",
    "None": None,
}


async def process_time_grouping(time_unit: TimeUnit) -> str | None:
    return time_groupings[time_unit.value]


async def process_groupby(
    groupby: Annotated[GroupBy, fastapi_query_groupby] = GroupBy.NoneValue,
) -> str | None:
    return await process_time_grouping(groupby)


async def process_frequency(
    frequency: Annotated[Frequency, fastapi_query_frequency] = Frequency.Hourly,
) -> str:
    return await process_time_grouping(frequency)  # type: ignore


async def process_start_time(
    start_time: Annotated[str | None, fastapi_query_start_time] = "2013-01-01",
    timezone: Annotated[Timezone, Depends(process_timezone)] = Timezone.UTC,  # type: ignore
):
    if start_time:
        if timezone:
            try:
                start_time = (
                    Timestamp(start_time, tz=timezone)
                    .tz_convert(ZoneInfo(TIMEZONE_UTC))
                    .tz_localize(None)
                )
            except Exception as exception:
                raise HTTPException(
                    status_code=400,
                    detail=str(exception),
                )
        else:
            try:
                start_time = Timestamp(start_time)
            except Exception as exception:
                raise HTTPException(
                    status_code=400,
                    detail=str(exception),
                )

    return start_time


async def process_end_time(
    end_time: Annotated[str | None, fastapi_query_end_time] = "2013-12-31",
    timezone: Annotated[Timezone, Depends(process_timezone)] = Timezone.UTC,  # type: ignore
):
    if end_time:
        if timezone:
            try:
                end_time = (
                    Timestamp(end_time, tz=timezone)
                    .tz_convert(ZoneInfo(TIMEZONE_UTC))
                    .tz_localize(None)
                )
            except Exception as exception:
                raise HTTPException(
                    status_code=400,
                    detail=str(exception),
                )
        else:
            try:
                end_time = Timestamp(end_time)
            except Exception as exception:
                raise HTTPException(
                    status_code=400,
                    detail=str(exception),
                )

    return end_time


async def process_timestamps(
    common_datasets: Annotated[dict, Depends(_provide_common_datasets)],
    timestamps_from_data: Annotated[
        bool, fastapi_query_use_timestamps_from_data
    ] = True,  # NOTE USED ONLY INTERNALLY FOR RESPECTING OR NOT THE DATA TIMESTAMPS ##### NOTE NOTE NOTE Re-name read_timestamps_from_data
    timestamps: Annotated[str | None, fastapi_query_timestamps] = None,
    start_time: Annotated[str | None, Depends(process_start_time)] = "2013-01-01",
    periods: Annotated[int | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, Depends(process_frequency)] = Frequency.Hourly,
    end_time: Annotated[str | None, Depends(process_end_time)] = "2013-12-31",
    timezone: Annotated[Optional[Timezone], Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
) -> DatetimeIndex:
    """ """
    if timestamps_from_data:
        data_file = None
        if any(
            [
                common_datasets["global_horizontal_irradiance_series"],
                common_datasets["direct_horizontal_irradiance_series"],
                common_datasets["spectral_factor_series"],
            ]
        ):
            data_file = next(
                filter(
                    None,
                    [
                        common_datasets["global_horizontal_irradiance_series"],
                        common_datasets["direct_horizontal_irradiance_series"],
                        common_datasets["spectral_factor_series"],
                    ],
                )
            )
    else:
        data_file = None

    if start_time is not None or end_time is not None or periods is not None:
        try:
            timestamps = generate_timestamps(
                data_file=data_file,
                start_time=start_time,
                end_time=end_time,
                periods=periods,  # type: ignore
                frequency=frequency,
                timezone=timezone,  # type: ignore[arg-type]
                name=None,
            )
        except Exception as exception:
            raise HTTPException(
                status_code=400,
                detail=str(exception),
            )

    if timestamps.tzinfo:  # type: ignore
        timestamps = timestamps.tz_localize(None)  # type: ignore

    return timestamps


async def process_timestamps_override_timestamps_from_data(
    common_datasets: Annotated[dict, Depends(_provide_common_datasets)],
    timestamps: Annotated[str | None, fastapi_query_timestamps] = None,
    start_time: Annotated[str | None, Depends(process_start_time)] = "2013-01-01",
    periods: Annotated[int | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, Depends(process_frequency)] = Frequency.Hourly,
    end_time: Annotated[str | None, Depends(process_end_time)] = "2013-12-31",
    timezone: Annotated[Optional[Timezone], Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
) -> DatetimeIndex:
    return await process_timestamps(
        common_datasets=common_datasets,
        timestamps_from_data=False,  # NOTE Override the default here
        timestamps=timestamps,
        start_time=start_time,
        periods=periods,
        frequency=frequency,
        end_time=end_time,
        timezone=timezone,
    )


async def create_temperature_series(
    temperature_series: float | None = None,
) -> TemperatureSeries:
    """ """
    if isinstance(temperature_series, float):
        return TemperatureSeries(
            value=np.array(temperature_series, dtype=np.float32),
            unit=SYMBOL_UNIT_TEMPERATURE,
        )

    return TemperatureSeries(
        value=np.array(TEMPERATURE_DEFAULT, dtype=np.float32),
        unit=SYMBOL_UNIT_TEMPERATURE,
    )


async def create_wind_speed_series(
    wind_speed_series: float | None = None,
) -> WindSpeedSeries:
    """ """
    if isinstance(wind_speed_series, float):
        return WindSpeedSeries(
            value=np.array(wind_speed_series), unit=SYMBOL_UNIT_WIND_SPEED
        )

    return WindSpeedSeries(
        value=np.array(WIND_SPEED_DEFAULT), unit=SYMBOL_UNIT_WIND_SPEED
    )


async def create_spectral_factor_series(
    spectral_factor_series: float | None = None,
) -> SpectralFactorSeries:
    """ """
    if isinstance(spectral_factor_series, float):
        return SpectralFactorSeries(
            value=np.array(spectral_factor_series, dtype=np.float32)
        )

    return SpectralFactorSeries(
        value=np.array(SPECTRAL_FACTOR_DEFAULT, dtype=np.float32)
    )


async def process_linke_turbidity_factor_series(
    linke_turbidity_factor_series: Annotated[
        float, fastapi_query_linke_turbidity_factor_series
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
) -> LinkeTurbidityFactor:
    """ """
    return LinkeTurbidityFactor(value=linke_turbidity_factor_series)


async def process_angle_output_units(
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_query_angle_output_units
    ] = AngleOutputUnit.RADIANS,
) -> str:
    """ """
    if angle_output_units.value == AngleOutputUnit.RADIANS.value:
        return RADIANS
    else:
        return DEGREES


async def process_refracted_solar_zenith(
    refracted_solar_zenith: Annotated[
        float, fastapi_query_refracted_solar_zenith
    ] = math.degrees(REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT),
) -> float:
    """ """
    return math.radians(refracted_solar_zenith)


async def process_surface_tilt_list(
    surface_tilt: Annotated[list[float], fastapi_query_surface_tilt_list] = [
        float(SURFACE_TILT_DEFAULT)
    ],
    surface_orientation: Annotated[
        list[float], fastapi_query_surface_orientation_list
    ] = [float(SURFACE_ORIENTATION_DEFAULT)],
) -> list[float]:
    """ """
    for surface_tilt_value in surface_tilt:
        if not SURFACE_TILT_MINIMUM <= surface_tilt_value <= SURFACE_TILT_MAXIMUM:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=400,
                detail=f"Value {surface_tilt_value} is out of the range {SURFACE_TILT_MINIMUM}-{SURFACE_TILT_MAXIMUM}.",
            )

    if len(surface_orientation) != len(surface_tilt):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="Surface tilt options and surface orientation options must have the same number of inputs",
        )

    return [math.radians(surface_tilt_value) for surface_tilt_value in surface_tilt]


async def process_surface_orientation_list(
    surface_tilt: Annotated[list[float], fastapi_query_surface_tilt_list] = [
        float(SURFACE_TILT_DEFAULT)
    ],
    surface_orientation: Annotated[
        list[float], fastapi_query_surface_orientation_list
    ] = [float(SURFACE_ORIENTATION_DEFAULT)],
) -> list[float]:
    """ """
    for surface_orientation_value in surface_orientation:
        if (
            not SURFACE_ORIENTATION_MINIMUM
            <= surface_orientation_value
            <= SURFACE_ORIENTATION_MAXIMUM
        ):
            from fastapi import HTTPException

            raise HTTPException(
                status_code=400,
                detail=f"Value {surface_orientation_value} is out of the range {SURFACE_ORIENTATION_MINIMUM}-{SURFACE_ORIENTATION_MAXIMUM}.",
            )

    if len(surface_orientation) != len(surface_tilt):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="Surface tilt options and surface orientation options must have the same number of inputs",
        )

    return [
        math.radians(surface_orientation_value)
        for surface_orientation_value in surface_orientation
    ]


async def process_series_solar_position_model(
    solar_position_model: Annotated[
        SolarPositionModel, fastapi_query_solar_position_model
    ] = SOLAR_POSITION_ALGORITHM_DEFAULT,
) -> SolarPositionModel:
    """ """
    NOT_IMPLEMENTED_MODELS = [
        SolarPositionModel.hofierka,
        SolarPositionModel.pvlib,
        SolarPositionModel.pysolar,
        SolarPositionModel.skyfield,
        SolarPositionModel.suncalc,
        SolarPositionModel.all,
    ]
    if solar_position_model in NOT_IMPLEMENTED_MODELS:
        models_bad_choices = ", ".join(model.value for model in NOT_IMPLEMENTED_MODELS)
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail=f"Models {models_bad_choices} are currently not supported.",
        )

    return solar_position_model


async def process_series_solar_position_models_list(
    solar_position_models: Annotated[
        List[SolarPositionModel], fastapi_query_solar_position_models
    ] = [SolarPositionModel.noaa],
) -> List[SolarPositionModel]:

    NOT_IMPLEMENTED_MODELS = [
        SolarPositionModel.hofierka,
        SolarPositionModel.pvlib,
        SolarPositionModel.pysolar,
        SolarPositionModel.skyfield,
        SolarPositionModel.suncalc,
        SolarPositionModel.all,
    ]

    for solar_position_model in solar_position_models:
        if solar_position_model in NOT_IMPLEMENTED_MODELS:
            models_bad_choices = ", ".join(
                model.value for model in NOT_IMPLEMENTED_MODELS
            )

            from fastapi import HTTPException

            raise HTTPException(
                status_code=400,
                detail=f"Models {models_bad_choices} are currently not supported.",
            )

    return solar_position_models


async def process_series_solar_incidence_model(
    solar_incidence_model: Annotated[
        SolarIncidenceModel, fastapi_query_solar_incidence_model
    ] = SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
) -> SolarIncidenceModel:
    """ """
    NOT_IMPLEMENTED_MODELS = [
        SolarIncidenceModel.pvis,
        SolarIncidenceModel.all,
    ]
    if solar_incidence_model in NOT_IMPLEMENTED_MODELS:
        models_bad_choices = ", ".join(model.value for model in NOT_IMPLEMENTED_MODELS)
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail=f"Models {models_bad_choices} are currently not supported.",
        )

    return solar_incidence_model


async def process_verbose_for_performance_analysis(
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    analysis: Annotated[AnalysisLevel, fastapi_query_analysis] = AnalysisLevel.Simple,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
):
    """ """
    if analysis.value != AnalysisLevel.NoneValue:
        if verbose < 7:
            verbose = 9

    return await process_verbose(
        verbose=verbose, quick_response_code=quick_response_code
    )


async def process_verbose(
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
) -> int:
    """ """
    if quick_response_code.value != QuickResponseCode.NoneValue:
        verbose = 9

    return verbose


async def process_quiet_for_performance_analysis(
    quiet: Annotated[bool, fastapi_query_quiet] = QUIET_FLAG_DEFAULT,
    analysis: Annotated[AnalysisLevel, fastapi_query_analysis] = AnalysisLevel.Simple,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
) -> bool:
    """ """
    if analysis.value != AnalysisLevel.NoneValue:
        quiet = True

    return await process_quiet(quiet=quiet, quick_response_code=quick_response_code)


async def process_quiet(
    quiet: Annotated[bool, fastapi_query_quiet] = QUIET_FLAG_DEFAULT,
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
) -> bool:
    """ """
    if quick_response_code.value != QuickResponseCode.NoneValue:
        quiet = True

    return quiet


async def process_fingerprint(
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
    fingerprint: Annotated[bool, fastapi_query_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    csv: Annotated[str | None, fastapi_query_csv] = None,
) -> bool:
    if quick_response_code.value != QuickResponseCode.NoneValue or csv:
        fingerprint = True

    return fingerprint


async def convert_timestamps_to_specified_timezone(
    timestamps: Annotated[str | None, Depends(process_timestamps)] = None,
    timezone: Annotated[Timezone, Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
    user_requested_timestamps: Annotated[None, fastapi_query_convert_timestamps] = None,
    timezone_for_calculations: Annotated[
        Timezone, Depends(process_timezone_to_be_converted)
    ] = Timezone.UTC,  # type: ignore[attr-defined]
) -> DatetimeIndex:
    if timestamps.tz != timezone_for_calculations:  # type: ignore[union-attr]
        user_requested_timestamps = timestamps.tz_localize(timezone_for_calculations).tz_convert(timezone)  # type: ignore[union-attr]

    user_requested_timestamps = user_requested_timestamps.tz_localize(None)  # type: ignore[attr-defined]

    return user_requested_timestamps


async def convert_timestamps_to_specified_timezone_override_timestamps_from_data(
    timestamps: Annotated[
        str | None, Depends(process_timestamps_override_timestamps_from_data)
    ] = None,
    timezone: Annotated[Timezone, Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
    user_requested_timestamps: Annotated[None, fastapi_query_convert_timestamps] = None,
    timezone_for_calculations: Annotated[
        Timezone, Depends(process_timezone_to_be_converted)
    ] = Timezone.UTC,  # type: ignore[attr-defined]
) -> DatetimeIndex:
    if timestamps.tz != timezone_for_calculations:  # type: ignore[union-attr]
        user_requested_timestamps = timestamps.tz_localize(timezone_for_calculations).tz_convert(timezone)  # type: ignore[union-attr]

    user_requested_timestamps = user_requested_timestamps.tz_localize(None)  # type: ignore[attr-defined]

    return user_requested_timestamps


async def process_horizon_profile(
    common_datasets: Annotated[dict, Depends(_provide_common_datasets)],
    horizon_profile: Annotated[str | None, fastapi_query_horizon_profile] = "PVGIS",
    longitude: Annotated[float, Depends(process_longitude)] = 8.628,
    latitude: Annotated[float, Depends(process_latitude)] = 45.812,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    if horizon_profile == "PVGIS":
        from pvgisprototype.api.series.utilities import select_location_time_series
        from pvgisprototype.api.utilities.conversions import (
            convert_float_to_degrees_if_requested,
        )

        horizon_profile = select_location_time_series(
            time_series=common_datasets["horizon_profile_series"],
            variable=None,
            coordinate=None,
            minimum=None,
            maximum=None,
            longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
            latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
            verbose=verbose,
        )

        return horizon_profile

    elif (
        horizon_profile == "None"
    ):  # NOTE WHY THIS IS HAPPENING? FASTAPI DOES NOT UNDERSTAND NONE VALUE!!!
        return None
    else:
        from numpy import fromstring

        try:
            horizon_profile_array = fromstring(
                horizon_profile, sep=","  # type: ignore[arg-type]
            )  # NOTE Parse user input
            _horizon_azimuth_radians = infer_horizon_azimuth_in_radians(
                horizon_profile_array
            )  # NOTE Process it
            horizon_profile = DataArray(  # type: ignore[assignment]
                radians(horizon_profile_array),
                coords={
                    "azimuth": _horizon_azimuth_radians,
                },
                dims=["azimuth"],
                name="horizon_height",
            )

            return horizon_profile

        except Exception as exception:
            raise HTTPException(
                status_code=400,
                detail=str(exception),
            )


async def process_horizon_profile_no_read(
    horizon_profile: Annotated[str | None, fastapi_query_horizon_profile] = "PVGIS",
):
    """Process horizon profile input. No read of a dataset is happening here,
    only preparation.
    - If `horizon_profile` is "PVGIS" then the function returns "PVGIS" and the reading
    of the data is going to happend in the `_read_datasets` asynchronous function
    - If `horizon_profile` is "None" then returns None and no data reading is going to
    happen in the `_read_datasets` asynchronous function
    - In any other case it is assumed that the user provided horizon heights so the `xarray.DataArray`
    is prepared and forward to the software. Again no data reading is going to happen in the
    `_read_datasets` asynchronous function

    Parameters
    ----------
    horizon_profile : Annotated[str  |  None, fastapi_query_horizon_profile], optional
        Horizon profile option, by default "PVGIS"
    """
    if horizon_profile == "PVGIS":
        return horizon_profile
    elif (
        horizon_profile == "None"
    ):  # NOTE WHY THIS IS HAPPENING? FASTAPI DOES NOT UNDERSTAND NONE VALUE!!!
        return None
    else:
        from numpy import fromstring

        try:
            horizon_profile_array = fromstring(
                horizon_profile, sep=","  # type: ignore[arg-type]
            )  # NOTE Parse user input
            _horizon_azimuth_radians = infer_horizon_azimuth_in_radians(
                horizon_profile_array
            )  # NOTE Process it
            horizon_profile = DataArray(  # type: ignore[assignment]
                radians(horizon_profile_array),
                coords={
                    "azimuth": _horizon_azimuth_radians,
                },
                dims=["azimuth"],
                name="horizon_height",
            )

            return horizon_profile

        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse option horizon_profile={horizon_profile}!",
            )


async def _read_datasets(
    common_datasets: Annotated[dict, Depends(_provide_common_datasets)],
    longitude: Annotated[float, Depends(process_longitude)] = 8.628,
    latitude: Annotated[float, Depends(process_latitude)] = 45.812,
    timestamps: Annotated[str | None, Depends(process_timestamps)] = None,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    horizon_profile: Annotated[
        str | None, Depends(process_horizon_profile_no_read)
    ] = "PVGIS",
):
    other_kwargs = {
        "neighbor_lookup": NEIGHBOR_LOOKUP_DEFAULT,
        "tolerance": TOLERANCE_DEFAULT,
        "mask_and_scale": MASK_AND_SCALE_FLAG_DEFAULT,
        "in_memory": IN_MEMORY_FLAG_DEFAULT,
        "dtype": DATA_TYPE_DEFAULT,
        "array_backend": ARRAY_BACKEND_DEFAULT,
        "multi_thread": MULTI_THREAD_FLAG_DEFAULT,
    }

    async with asyncio.TaskGroup() as task_group:

        temperature_task = task_group.create_task(
            asyncio.to_thread(
                get_temperature_series,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                temperature_series=common_datasets["temperature_series"],
                verbose=verbose,
                **other_kwargs,  # type: ignore
            )
        )
        wind_speed_task = task_group.create_task(
            asyncio.to_thread(
                get_wind_speed_series,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                wind_speed_series=common_datasets["wind_speed_series"],
                verbose=verbose,
                **other_kwargs,  # type: ignore
            )
        )
        global_horizontal_irradiance_task = task_group.create_task(
            asyncio.to_thread(
                get_global_horizontal_irradiance_series,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                global_horizontal_irradiance_series=common_datasets[
                    "global_horizontal_irradiance_series"
                ],
                verbose=verbose,
                **other_kwargs,  # type: ignore
            )
        )
        direct_horizontal_irradiance_task = task_group.create_task(
            asyncio.to_thread(
                get_direct_horizontal_irradiance_series,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                direct_horizontal_irradiance_series=common_datasets[
                    "direct_horizontal_irradiance_series"
                ],
                verbose=verbose,
                **other_kwargs,  # type: ignore
            )
        )
        spectral_factor_task = task_group.create_task(
            asyncio.to_thread(
                get_spectral_factor_series,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                spectral_factor_series=common_datasets["spectral_factor_series"],
                verbose=verbose,
                **other_kwargs,  # type: ignore
            )
        )

        if not isinstance(horizon_profile, DataArray):
            if horizon_profile == "PVGIS":
                from pvgisprototype.api.series.utilities import (
                    select_location_time_series,
                )
                from pvgisprototype.api.utilities.conversions import (
                    convert_float_to_degrees_if_requested,
                )

                horizon_profile_task = task_group.create_task(
                    asyncio.to_thread(
                        select_location_time_series,
                        time_series=common_datasets["horizon_profile_series"],
                        variable=None,
                        coordinate=None,
                        minimum=None,
                        maximum=None,
                        longitude=convert_float_to_degrees_if_requested(
                            longitude, DEGREES
                        ),
                        latitude=convert_float_to_degrees_if_requested(
                            latitude, DEGREES
                        ),
                        verbose=verbose,
                    )
                )

    return {
        "global_horizontal_irradiance_series": global_horizontal_irradiance_task.result(),
        "direct_horizontal_irradiance_series": direct_horizontal_irradiance_task.result(),
        "temperature_series": temperature_task.result(),
        "wind_speed_series": wind_speed_task.result(),
        "spectral_factor_series": spectral_factor_task.result(),
        "horizon_profile": (
            horizon_profile
            if (isinstance(horizon_profile, DataArray) or (horizon_profile is None))
            else horizon_profile_task.result()
        ),
    }


async def process_shading_model(
    shading_model: Annotated[
        ShadingModel, fastapi_query_shading_model
    ] = ShadingModel.pvis,
):
    NOT_IMPLEMENTED = [
        ShadingModel.all,
        ShadingModel.pvlib,
    ]

    if shading_model in NOT_IMPLEMENTED:
        raise HTTPException(
            status_code=400,
            detail=f"Option '{shading_model.name}' is not currently supported!",
        )

    return shading_model


async def process_surface_position_optimisation_method(
    surface_position_optimisation_method: Annotated[
        SurfacePositionOptimizerMethod,
        fastapi_query_surface_position_optimisation_method,
    ] = SurfacePositionOptimizerMethod.l_bfgs_b,
):
    NOT_IMPLEMENTED = [
        SurfacePositionOptimizerMethod.powell,
        SurfacePositionOptimizerMethod.nelder_mead,
        SurfacePositionOptimizerMethod.direct,
    ]

    if surface_position_optimisation_method in NOT_IMPLEMENTED:
        raise HTTPException(
            status_code=400,
            detail=f"Option '{surface_position_optimisation_method.name}' is not currently supported!",
        )

    return surface_position_optimisation_method


async def process_optimise_surface_position(
    _read_datasets: Annotated[dict, Depends(_read_datasets)],
    longitude: Annotated[float, Depends(process_longitude)] = 8.628,
    latitude: Annotated[float, Depends(process_latitude)] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[
        float, Depends(process_surface_orientation)
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[
        float, Depends(process_surface_tilt)
    ] = SURFACE_TILT_DEFAULT,
    start_time: Annotated[str | None, fastapi_query_start_time] = "2013-01-01",
    periods: Annotated[int | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, Depends(process_frequency)] = Frequency.Hourly,
    end_time: Annotated[str | None, fastapi_query_end_time] = "2013-12-31",
    timestamps: Annotated[str | None, Depends(process_timestamps)] = None,
    timezone: Annotated[Timezone, Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
    timezone_for_calculations: Annotated[Timezone, Depends(process_timezone_to_be_converted)] = Timezone.UTC,  # type: ignore[attr-defined]
    user_requested_timestamps: Annotated[
        None, Depends(convert_timestamps_to_specified_timezone)
    ] = None,
    shading_model: Annotated[
        ShadingModel, Depends(process_shading_model)
    ] = ShadingModel.pvis,
    linke_turbidity_factor_series: Annotated[
        float | LinkeTurbidityFactor, Depends(process_linke_turbidity_factor_series)
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model
    ] = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    surface_position_optimisation_mode: Annotated[
        SurfacePositionOptimizerMode, fastapi_query_surface_position_optimisation_mode
    ] = SurfacePositionOptimizerMode.NoneValue,
    surface_position_optimisation_method: Annotated[
        SurfacePositionOptimizerMethod,
        Depends(process_surface_position_optimisation_method),
    ] = SurfacePositionOptimizerMethod.l_bfgs_b,
    sampling_method_shgo: Annotated[
        SurfacePositionOptimizerMethodSHGOSamplingMethod,
        fastapi_query_sampling_method_shgo,
    ] = SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
    number_of_sampling_points: Annotated[
        int, fastapi_query_number_of_samping_points
    ] = NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    iterations: Annotated[int, fastapi_query_iterations] = NUMBER_OF_ITERATIONS_DEFAULT,
    fingerprint: Annotated[
        bool, Depends(process_fingerprint)
    ] = FINGERPRINT_FLAG_DEFAULT,
) -> dict:
    """ """
    if surface_position_optimisation_mode == SurfacePositionOptimizerMode.NoneValue:
        return {}
    else:
        optimal_surface_position = optimise_surface_position(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            min_surface_orientation=SurfaceOrientation().min_radians,
            max_surface_orientation=SurfaceOrientation().max_radians,
            min_surface_tilt=SurfaceTilt().min_radians,
            max_surface_tilt=SurfaceTilt().max_radians,
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
            timestamps=timestamps,
            timezone=timezone_for_calculations,  # type: ignore
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            photovoltaic_module=photovoltaic_module,
            mode=surface_position_optimisation_mode,
            method=surface_position_optimisation_method,
            sampling_method_shgo=sampling_method_shgo,
            number_of_sampling_points=number_of_sampling_points,
            iterations=iterations,
            fingerprint=fingerprint,
        )

        if (optimal_surface_position["Surface Tilt"] is None) or (  # type: ignore
            optimal_surface_position["Surface Orientation"] is None  # type: ignore
        ):
            raise HTTPException(
                status_code=400,
                detail="Using combination of input could not find optimal surface position",
            )

        return optimal_surface_position  # type: ignore


async def _select_data_from_meteorological_variable(
    common_datasets: Annotated[dict, Depends(_provide_common_datasets)],
    meteorological_variable: Annotated[
        MeteorologicalVariable, fastapi_query_meteorological_variable
    ] = MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE,
    longitude: Annotated[float, fastapi_query_longitude_in_degrees] = 8.628,
    latitude: Annotated[float, fastapi_query_latitude_in_degrees] = 45.812,
    timestamps: Annotated[str | None, Depends(process_timestamps)] = None,
    start_time: Annotated[
        str | None, fastapi_query_start_time
    ] = "2010-01-01",  # Used by fastapi_query_start_time
    periods: Annotated[
        int | None, fastapi_query_periods
    ] = None,  # Used by fastapi_query_periods
    frequency: Annotated[Frequency, Depends(process_frequency)] = Frequency.Hourly,
    end_time: Annotated[
        str | None, fastapi_query_end_time
    ] = "2020-12-31",  # Used by fastapi_query_end_time
    neighbor_lookup: Annotated[
        MethodForInexactMatches, fastapi_query_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float, fastapi_query_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, fastapi_query_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, fastapi_query_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    verbose: Annotated[int, Depends(process_verbose)] = VERBOSE_LEVEL_DEFAULT,
):
    meteorological_variable_file_mapping = {
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: common_datasets[
            "temperature_series"
        ],
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: common_datasets[
            "global_horizontal_irradiance_series"
        ],
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: None,
        MeteorologicalVariable.MEAN_WIND_SPEED: common_datasets["wind_speed_series"],
        MeteorologicalVariable.MEAN_DEW_POINT_TEMPERATURE: None,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: None,
        MeteorologicalVariable.MAX_DEW_POINT_TEMPERATURE: None,
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: None,
        MeteorologicalVariable.MAX_WIND_SPEED: None,
        MeteorologicalVariable.MIN_DEW_POINT_TEMPERATURE: None,
        MeteorologicalVariable.all: None,
    }

    file_variable_mapping = {
        common_datasets["temperature_series"]: "era5_t2m",
        common_datasets["wind_speed_series"]: "era5_ws2m",
        common_datasets["global_horizontal_irradiance_series"]: "sarah3_sis",
        common_datasets["direct_horizontal_irradiance_series"]: "sarah3_sid",
    }  # NOTE Add more here...

    if meteorological_variable_file_mapping[meteorological_variable]:
        variable = file_variable_mapping[
            meteorological_variable_file_mapping[meteorological_variable]
        ]
        data_array = select_time_series(
            time_series=meteorological_variable_file_mapping[meteorological_variable],
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            mask_and_scale=mask_and_scale,  # True ?
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            in_memory=in_memory,
            verbose=verbose,
        )

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Option {meteorological_variable} is not currently supported!",
        )  # NOTE This MUST be removed when all data will be supported!

    return {
        "variable": variable,
        "data_array": data_array,
    }


async def tmy_statistic_model(
    plot_statistic: Annotated[
        TMYStatisticModel | None, fastapi_query_tmy_statistic_model  # type: ignore
    ] = None,
) -> TMYStatisticModel:  # type: ignore

    NOT_IMPLEMENTED_YET = [
        TMYStatisticModel.ranked,
        TMYStatisticModel.weighted,
        TMYStatisticModel.finkelsteinschafer,
        TMYStatisticModel.yearly_ecdf,
        TMYStatisticModel.long_term_ecdf,
        TMYStatisticModel.all,
    ]

    if plot_statistic in NOT_IMPLEMENTED_YET:
        raise HTTPException(
            status_code=400,
            detail=f"Option {plot_statistic} is not currently supported!",
        )

    return plot_statistic


fastapi_dependable_longitude = Depends(process_longitude)
fastapi_dependable_latitude = Depends(process_latitude)
fastapi_dependable_surface_orientation = Depends(process_surface_orientation)
fastapi_dependable_surface_tilt = Depends(process_surface_tilt)
fastapi_dependable_timezone = Depends(process_timezone)
fastapi_dependable_timestamps = Depends(process_timestamps)
fastapi_dependable_temperature_series = Depends(create_temperature_series)
fastapi_dependable_wind_speed_series = Depends(create_wind_speed_series)
fastapi_dependable_spectral_factor_series = Depends(create_spectral_factor_series)
fastapi_dependable_groupby = Depends(process_groupby)
fastapi_dependable_frequency = Depends(process_frequency)
fastapi_dependable_linke_turbidity_factor_series = Depends(
    process_linke_turbidity_factor_series
)
fastapi_dependable_angle_output_units = Depends(process_angle_output_units)
fastapi_dependable_refracted_solar_zenith = Depends(process_refracted_solar_zenith)
fastapi_dependable_surface_orientation_list = Depends(process_surface_orientation_list)
fastapi_dependable_surface_tilt_list = Depends(process_surface_tilt_list)
fastapi_dependable_solar_position_models = Depends(process_series_solar_position_model)
fastapi_dependable_solar_incidence_models = Depends(
    process_series_solar_incidence_model
)
fastapi_dependable_verbose = Depends(process_verbose)
fastapi_dependable_verbose_for_performance_analysis = Depends(
    process_verbose_for_performance_analysis
)
fastapi_dependable_quiet = Depends(process_quiet)
fastapi_dependable_quiet_for_performance_analysis = Depends(
    process_quiet_for_performance_analysis
)
fastapi_dependable_fingerprint = Depends(process_fingerprint)
fastapi_dependable_optimise_surface_position = Depends(
    process_optimise_surface_position
)
fastapi_dependable_convert_timestamps = Depends(
    convert_timestamps_to_specified_timezone
)
fastapi_dependable_convert_timezone = Depends(process_timezone_to_be_converted)
fastapi_dependable_common_datasets = Depends(_provide_common_datasets)

fastapi_dependable_start_time = Depends(process_start_time)
fastapi_dependable_end_time = Depends(process_start_time)

fastapi_dependable_read_datasets = Depends(_read_datasets)

fastapi_dependable_solar_position_models_list = Depends(
    process_series_solar_position_models_list
)
fastapi_dependable_horizon_profile = Depends(process_horizon_profile)
fastapi_dependable_shading_model = Depends(process_shading_model)

fastapi_dependable_select_data_from_meteorological_variable = Depends(
    _select_data_from_meteorological_variable
)
fastapi_dependable_tmy_statistic_model = Depends(tmy_statistic_model)
