import math
from typing import Annotated, Optional
from zoneinfo import ZoneInfo

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
from pvgisprototype.api.position.models import (
    SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SolarIncidenceModel,
    SolarPositionModel,
)
from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.api.utilities.timestamp import (
    generate_datetime_series,
    parse_timestamp_series,
)
from pvgisprototype.constants import (
    DEGREES,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
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
    WIND_SPEED_DEFAULT,
)
from pvgisprototype.web_api.fastapi_parameters import (
    fastapi_query_angle_output_units,
    fastapi_query_end_time,
    fastapi_query_frequency,
    fastapi_query_groupby,
    fastapi_query_latitude,
    fastapi_query_linke_turbidity_factor_series,
    fastapi_query_longitude,
    fastapi_query_periods,
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
)
from pvgisprototype.web_api.schemas import AngleOutputUnit, Frequency, GroupBy, Timezone
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_quick_response_code
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_quiet
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_verbose
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_analysis
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_fingerprint
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_csv
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT
from pvgisprototype.constants import QUIET_FLAG_DEFAULT
from pvgisprototype.constants import QUICK_RESPONSE_CODE_FLAG_DEFAULT
from pvgisprototype.constants import ANALYSIS_FLAG_DEFAULT


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


async def process_groupby(
    groupby: Annotated[GroupBy, fastapi_query_groupby] = GroupBy.N,
) -> str | None:

    time_groupings = {
        "Yearly": "Y",
        "Seasonal": "S",
        "Monthly": "M",
        "Weekly": "W",
        "Daily": "D",
        "Hourly": "h",
        "Do not group by": None,
    }
    return time_groupings[groupby.value]


async def process_frequency(
    frequency: Annotated[Frequency, fastapi_query_frequency] = Frequency.Hour,
) -> str:

    time_groupings = {
        "Yearly": "Y",
        "Seasonal": "S",
        "Monthly": "M",
        "Weekly": "W",
        "Daily": "D",
        "Hourly": "h",
    }
    return time_groupings[frequency.value]


async def process_series_timestamp(
    timestamps: Annotated[str | None, fastapi_query_timestamps] = None,
    start_time: Annotated[str | None, fastapi_query_start_time] = None,
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, Depends(process_frequency)] = Frequency.Hour,
    end_time: Annotated[str | None, fastapi_query_end_time] = None,
    timezone: Annotated[Optional[Timezone], Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
) -> DatetimeIndex:

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
                    detail=f"Timestamps {timestamps_str} is not a valid input.",
                )

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

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

    return timestamps


async def create_temperature_series(
    temperature_series: Optional[float] = None,
) -> TemperatureSeries:
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
    return LinkeTurbidityFactor(value=linke_turbidity_factor_series)


async def process_angle_output_units(
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_query_angle_output_units
    ] = AngleOutputUnit.RADIANS
) -> str:
    if angle_output_units.value == AngleOutputUnit.RADIANS.value:
        return RADIANS
    else:
        return DEGREES


async def process_refracted_solar_zenith(
    refracted_solar_zenith: Annotated[
        float, fastapi_query_refracted_solar_zenith
    ] = math.degrees(REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT)
) -> float:
    return math.radians(refracted_solar_zenith)


async def process_surface_tilt_list(
    surface_tilt: Annotated[list[float], fastapi_query_surface_tilt_list] = [
        float(SURFACE_TILT_DEFAULT)
    ],
    surface_orientation: Annotated[
        list[float], fastapi_query_surface_orientation_list
    ] = [float(SURFACE_ORIENTATION_DEFAULT)],
) -> list[float]:
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
        quick_response_code: Annotated[bool, fastapi_query_quick_response_code] = QUICK_RESPONSE_CODE_FLAG_DEFAULT,
        verbose: Annotated[int, fastapi_query_verbose] = VERBOSE_LEVEL_DEFAULT,
        analysis: Annotated[bool, fastapi_query_analysis] = ANALYSIS_FLAG_DEFAULT,
) -> int:
    
    if quick_response_code:
        verbose = 9
    
    if analysis:
        verbose = 9

    return verbose 


async def process_quiet(
        quick_response_code: Annotated[bool, fastapi_query_quick_response_code] = QUICK_RESPONSE_CODE_FLAG_DEFAULT,
        quiet: Annotated[bool, fastapi_query_quiet] = QUIET_FLAG_DEFAULT,
) -> bool:
    
    if quick_response_code:
        quiet = True
    
    return quiet


async def process_fingerprint(
        quick_response_code: Annotated[bool, fastapi_query_quick_response_code] = QUICK_RESPONSE_CODE_FLAG_DEFAULT,
        fingerprint: Annotated[bool, fastapi_query_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
        csv: Annotated[bool,fastapi_query_csv] = False,
) -> bool:
    
    if quick_response_code:
        fingerprint = True
    
    if csv:
        fingerprint = True

    return fingerprint

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
fastapi_dependable_linke_turbidity_factor_series = Depends(process_linke_turbidity_factor_series)
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