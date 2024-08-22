import math
from typing import Annotated, Dict, Optional, TypeVar
from zoneinfo import ZoneInfo
from pathlib import Path
import numpy as np
from fastapi import Depends, HTTPException
from pandas import DatetimeIndex

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
from pvgisprototype.api.datetime.datetimeindex import (
    generate_datetime_series,
    parse_timestamp_series,
)
from pvgisprototype.api.position.models import (
    SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SolarIncidenceModel,
    SolarPositionModel,
)
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.api.surface.optimize_angles import optimize_angles
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMethodSHGOSamplingMethod, SurfacePositionOptimizerMode
from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.constants import (
    DEGREES,
    FINGERPRINT_FLAG_DEFAULT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
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
    VERBOSE_LEVEL_DEFAULT,
    WIND_SPEED_DEFAULT,
)
from pvgisprototype.web_api.fastapi_parameters import (
    fastapi_query_analysis,
    fastapi_query_angle_output_units,
    fastapi_query_csv,
    fastapi_query_elevation,
    fastapi_query_end_time,
    fastapi_query_fingerprint,
    fastapi_query_frequency,
    fastapi_query_groupby,
    fastapi_query_latitude,
    fastapi_query_linke_turbidity_factor_series,
    fastapi_query_longitude,
    fastapi_query_optimise_surface_position,
    fastapi_query_periods,
    fastapi_query_photovoltaic_module_model,
    fastapi_query_quick_response_code,
    fastapi_query_quiet,
    fastapi_query_refracted_solar_zenith,
    fastapi_query_solar_incidence_model,
    fastapi_query_solar_position_model,
    fastapi_query_start_time,
    fastapi_query_surface_orientation,
    fastapi_query_surface_orientation_list,
    fastapi_query_surface_tilt,
    fastapi_query_surface_tilt_list,
    fastapi_query_timestamps,
    fastapi_query_timezone,
    fastapi_query_verbose,
    fastapi_query_sampling_method_shgo,
)
from pvgisprototype.web_api.schemas import (
    AnalysisLevel,
    AngleOutputUnit,
    Frequency,
    GroupBy,
    Timezone,
)


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


async def process_timezone(
    timezone: Annotated[Timezone, fastapi_query_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
) -> ZoneInfo:
    return ZoneInfo(timezone.value)


TimeUnit = TypeVar("TimeUnit", GroupBy, Frequency)

time_groupings: Dict[str, Optional[str]] = {
    "Yearly": "YE",
    "Seasonal": "S",
    "Monthly": "ME",
    "Weekly": "W",
    "Daily": "D",
    "Hourly": "h",
    "Minutely": "min",
    "None": None,
}


async def process_time_grouping(time_unit: TimeUnit) -> Optional[str]:
    return time_groupings[time_unit.value]


async def process_groupby(
    groupby: Annotated[GroupBy, fastapi_query_groupby] = GroupBy.NoneValue,
) -> Optional[str]:
    return await process_time_grouping(groupby)


async def process_frequency(
    frequency: Annotated[Frequency, fastapi_query_frequency] = Frequency.Hourly,
) -> str:
    return await process_time_grouping(frequency)


async def process_series_timestamp(
    timestamps: Annotated[str | None, fastapi_query_timestamps] = None,
    start_time: Annotated[str | None, fastapi_query_start_time] = "2013-01-01",
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, Depends(process_frequency)] = Frequency.Hourly,
    end_time: Annotated[str | None, fastapi_query_end_time] = "2013-12-31",
    timezone: Annotated[Optional[Timezone], Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
) -> DatetimeIndex:
    """ """
    if start_time is None and end_time is None and timestamps is None:
        raise HTTPException(
            status_code=400, detail="Provide a valid start and end time or a timestamp"
        )

    if timestamps is None and (start_time is None or end_time is None):
        raise HTTPException(
            status_code=400, detail="Provide a valid start and end time or a timestamp"
        )

    if timestamps is not None and (not start_time or not end_time):
        try:
            timestamps_str = timestamps
            timestamps = parse_timestamp_series(timestamps=timestamps)  # type: ignore
            if timestamps.isna().any():  # type: ignore
                raise HTTPException(
                    status_code=400,
                    detail=f"Timestamps {timestamps_str} is not a valid input",
                )

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    if end_time is not None and start_time is None:
        raise HTTPException(
            status_code=400, detail="Provide a valid start and end time or a timestamp"
        )

    if start_time is not None and end_time is not None:
        try:
            timestamps = generate_datetime_series(
                start_time=start_time,
                end_time=end_time,
                periods=periods,
                frequency=frequency,  # type: ignore
                timezone=None,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    if timestamps.empty:  # type: ignore
        raise HTTPException(
            status_code=400,
            detail=f"Combination of options {start_time}, {end_time}, {frequency}, {periods} is not valid",
        )

    return timestamps


async def create_temperature_series(
    temperature_series: Optional[float] = None,
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
    wind_speed_series: Optional[float] = None,
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


async def process_verbose(
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
    verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
    analysis: Annotated[AnalysisLevel, fastapi_query_analysis] = AnalysisLevel.Simple,
) -> int:
    """ """
    if analysis.value != AnalysisLevel.NoneValue:
        verbose = 9

    if quick_response_code.value != QuickResponseCode.NoneValue:
        verbose = 9

    return verbose


async def process_quiet(
    quick_response_code: Annotated[
        QuickResponseCode, fastapi_query_quick_response_code
    ] = QuickResponseCode.NoneValue,
    quiet: Annotated[bool, fastapi_query_quiet] = QUIET_FLAG_DEFAULT,
    analysis: Annotated[AnalysisLevel, fastapi_query_analysis] = AnalysisLevel.Simple,
) -> bool:
    """ """
    if quick_response_code.value != QuickResponseCode.NoneValue:
        quiet = True

    if analysis.value != AnalysisLevel.NoneValue:
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


async def process_optimise_surface_position(
    longitude: Annotated[float, Depends(process_longitude)] = 8.628,
    latitude: Annotated[float, Depends(process_latitude)] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[
        float, Depends(process_surface_orientation)
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[
        float, Depends(process_surface_tilt)
    ] = SURFACE_TILT_DEFAULT,
    start_time: Annotated[str | None, fastapi_query_start_time] = None,
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, Depends(process_frequency)] = Frequency.Hourly,
    end_time: Annotated[str | None, fastapi_query_end_time] = None,
    timestamps: Annotated[str | None, Depends(process_series_timestamp)] = None,
    timezone: Annotated[Timezone, Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
    spectral_factor_series: Annotated[
        SpectralFactorSeries, Depends(create_spectral_factor_series)
    ] = None,
    linke_turbidity_factor_series: Annotated[
        float | LinkeTurbidityFactor, Depends(process_linke_turbidity_factor_series)
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model
    ] = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    optimise_surface_position: Annotated[
        SurfacePositionOptimizerMode, fastapi_query_optimise_surface_position
    ] = SurfacePositionOptimizerMode.NoneValue,
    sampling_method_shgo: Annotated[
        SurfacePositionOptimizerMethodSHGOSamplingMethod, fastapi_query_sampling_method_shgo
    ] = SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
) -> dict:
    """
    """
    if optimise_surface_position == SurfacePositionOptimizerMode.NoneValue:
        return {}
    else:
        if optimise_surface_position == SurfacePositionOptimizerMode.Orientation:
            optimise_surface_position = optimize_angles(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                min_surface_orientation=SurfaceOrientation().min_radians,
                max_surface_orientation=SurfaceOrientation().max_radians,
                min_surface_tilt=SurfaceTilt().min_radians,
                max_surface_tilt=SurfaceTilt().max_radians,
                timestamps=timestamps,
                timezone=timezone,  # type: ignore
                global_horizontal_irradiance = Path("sarah2_sis_over_esti_jrc.nc"),  # FIXME This hardwritten path will be replaced
                direct_horizontal_irradiance = Path("sarah2_sid_over_esti_jrc.nc"),  # FIXME This hardwritten path will be replaced
                spectral_factor_series = Path("spectral_effect_cSi_2013_over_esti_jrc.nc"),
                temperature_series = Path("era5_t2m_over_esti_jrc.nc"), # FIXME This hardwritten path will be replaced
                wind_speed_series = Path("era5_ws2m_over_esti_jrc.nc"), # FIXME This hardwritten path will be replaced
                linke_turbidity_factor_series = LinkeTurbidityFactor(value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
                photovoltaic_module=photovoltaic_module,
                mode=SurfacePositionOptimizerMode.Orientation,
                sampling_method_shgo=sampling_method_shgo,
            )
        elif optimise_surface_position == SurfacePositionOptimizerMode.Tilt:
            optimise_surface_position = optimize_angles(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                min_surface_orientation=SurfaceOrientation().min_radians,
                max_surface_orientation=SurfaceOrientation().max_radians,
                min_surface_tilt=SurfaceTilt().min_radians,
                max_surface_tilt=SurfaceTilt().max_radians,
                global_horizontal_irradiance=Path("sarah2_sis_over_esti_jrc.nc"),  # FIXME This hardwritten path will be replaced
                direct_horizontal_irradiance=Path("sarah2_sid_over_esti_jrc.nc"),  # FIXME This hardwritten path will be replaced
                timestamps=timestamps,
                timezone=timezone,  # type: ignore
                spectral_factor_series=spectral_factor_series,
                temperature_series=TemperatureSeries(value=TEMPERATURE_DEFAULT),
                wind_speed_series=WindSpeedSeries(value=WIND_SPEED_DEFAULT),
                linke_turbidity_factor_series=LinkeTurbidityFactor(
                    value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT
                ),
                photovoltaic_module=photovoltaic_module,
                mode=SurfacePositionOptimizerMode.Tilt,
                sampling_method_shgo=sampling_method_shgo,
            )
        else:
            optimise_surface_position = optimize_angles(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                min_surface_orientation=SurfaceOrientation().min_radians,
                max_surface_orientation=SurfaceOrientation().max_radians,
                min_surface_tilt=SurfaceTilt().min_radians,
                max_surface_tilt=SurfaceTilt().max_radians,
                global_horizontal_irradiance=Path("sarah2_sis_over_esti_jrc.nc"),  # FIXME This hardwritten path will be replaced
                direct_horizontal_irradiance=Path("sarah2_sid_over_esti_jrc.nc"),  # FIXME This hardwritten path will be replaced
                timestamps=timestamps,
                timezone=timezone,  # type: ignore
                spectral_factor_series=spectral_factor_series,
                temperature_series=TemperatureSeries(value=TEMPERATURE_DEFAULT),
                wind_speed_series=WindSpeedSeries(value=WIND_SPEED_DEFAULT),
                linke_turbidity_factor_series=LinkeTurbidityFactor(
                    value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT
                ),
                photovoltaic_module=photovoltaic_module,
                mode=SurfacePositionOptimizerMode.Tilt_and_Orientation,
                sampling_method_shgo=sampling_method_shgo,
            )

        if (optimise_surface_position["surface_tilt"] is None) or (
            optimise_surface_position["surface_orientation"] is None
        ):  # type: ignore
            raise HTTPException(
                status_code=400,
                detail="Using combination of input could not find optimal surface position",
            )

        return optimise_surface_position  # type: ignore


fastapi_dependable_longitude = Depends(process_longitude)
fastapi_dependable_latitude = Depends(process_latitude)
fastapi_dependable_surface_orientation = Depends(process_surface_orientation)
fastapi_dependable_surface_tilt = Depends(process_surface_tilt)
fastapi_dependable_timezone = Depends(process_timezone)
fastapi_dependable_timestamps = Depends(process_series_timestamp)
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
fastapi_dependable_quite = Depends(process_quiet)
fastapi_dependable_fingerprint = Depends(process_fingerprint)
fastapi_dependable_optimise_surface_position = Depends(
    process_optimise_surface_position
)
