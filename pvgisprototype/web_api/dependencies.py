import pandas as pd
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from typing import Annotated
from fastapi import Query
from fastapi import HTTPException
from fastapi import Depends
from pandas import DatetimeIndex

from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import convert_to_timezone
from pvgisprototype.api.utilities.timestamp import attach_requested_timezone
from pvgisprototype.api.utilities.timestamp import parse_timestamp_series
from pvgisprototype.api.utilities.timestamp import generate_datetime_series
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_longitude
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_latitude
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_surface_orientation
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_surface_tilt
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_timezone
from pvgisprototype.web_api.schemas import Timezone

from pvgisprototype import TemperatureSeries
from pvgisprototype import WindSpeedSeries
from pvgisprototype import SpectralFactorSeries
from pvgisprototype import SurfaceTilt
from pvgisprototype import SurfaceOrientation
from pvgisprototype import Latitude
from pvgisprototype import Longitude

from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype.constants import SYMBOL_UNIT_TEMPERATURE
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype.constants import SYMBOL_UNIT_WIND_SPEED
from pvgisprototype.constants import SPECTRAL_FACTOR_DEFAULT
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_start_time
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_periods
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_frequency
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_end_time
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_timestamps
from pvgisprototype.web_api.schemas import Timezone
from pvgisprototype.web_api.schemas import Frequency
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_groupby
from pvgisprototype.web_api.schemas import GroupBy
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_linke_turbidity_factor_series
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_angle_output_units
from pvgisprototype.web_api.schemas import AngleOutputUnit
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import DEGREES
import math
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_refracted_solar_zenith
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_surface_tilt_list
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_surface_orientation_list
from pvgisprototype.constants import SURFACE_ORIENTATION_MAXIMUM
from pvgisprototype.constants import SURFACE_ORIENTATION_MINIMUM
from pvgisprototype.constants import SURFACE_TILT_MAXIMUM
from pvgisprototype.constants import SURFACE_TILT_MINIMUM

async def process_longitude(
    longitude: Annotated[float, fastapi_query_longitude] = 8.628,
) -> Longitude:
    #return Longitude(value = convert_to_radians_fastapi(longitude), unit = RADIANS) # FIXME Revert to this when pydantic objects will be created
    return convert_to_radians_fastapi(longitude)


async def process_latitude(
    latitude: Annotated[float, fastapi_query_latitude] = 45.812,
) -> Latitude:
    #return Latitude(value = convert_to_radians_fastapi(latitude), unit = RADIANS) # FIXME Revert to this when pydantic objects will be created
    return convert_to_radians_fastapi(latitude)


async def process_surface_orientation(
    surface_orientation: Annotated[float, fastapi_query_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
) -> SurfaceOrientation:
    #return SurfaceOrientation(value = convert_to_radians_fastapi(surface_orientation), unit = RADIANS) # FIXME Revert to this when pydantic objects will be created
    return convert_to_radians_fastapi(surface_orientation)


async def process_surface_tilt(
    surface_tilt: Annotated[float, fastapi_query_surface_tilt] = SURFACE_TILT_DEFAULT,
) -> SurfaceTilt:
    #return SurfaceTilt(value = convert_to_radians_fastapi(surface_tilt), unit = RADIANS) # FIXME Revert to this when pydantic objects will be created
    return convert_to_radians_fastapi(surface_tilt)


async def process_timezone(
        timezone: Annotated[Timezone, fastapi_query_timezone] = Timezone.UTC, # type: ignore[attr-defined]
) -> ZoneInfo:
    return ZoneInfo(timezone.value)


async def process_series_timestamp(
    timestamps: Annotated[str | None, fastapi_query_timestamps] = None, 
    start_time: Annotated[str | None, fastapi_query_start_time] = None,
    periods: Annotated[str | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, fastapi_query_frequency] = Frequency.H,
    end_time: Annotated[str | None, fastapi_query_end_time] = None,
    timezone:  Annotated[Optional[Timezone], Depends(process_timezone)] = Timezone.UTC, # type: ignore[attr-defined]
) -> DatetimeIndex:

    if start_time is None and end_time is None and timestamps is None:
        raise HTTPException(status_code=400, detail="Provide a valid start and end time or a timestamp")
    
    if timestamps is None and (start_time is None or end_time is None):
        raise HTTPException(status_code=400, detail="Provide a valid start and end time or a timestamp")
    
    if timestamps is not None and (not start_time or not end_time):
        try:
            timestamps_str = timestamps
            timestamps = parse_timestamp_series(timestamps=timestamps)
            if timestamps.isna().any():
                    raise HTTPException(status_code=400, detail=f"Timestamps {timestamps_str} is not a valid input.")

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    if start_time is not None and end_time is not None:
        try:
            timestamps = generate_datetime_series(
                start_time=start_time,
                end_time=end_time,
                periods=periods,
                frequency=frequency.value,
                timezone = None,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    return timestamps


async def process_groupby(
        group_by: Annotated[GroupBy, fastapi_query_groupby] = GroupBy.N,
) -> str | None:
    
    time_groupings = {
        "Yearly": "Y",
        "Seasonly": "S",
        "Monthly": "M",
        'Weekly': "W",
        'Daily': "D",
        'Hourly': "h",
        "Do not group by": None
        }
    
    return time_groupings[group_by.value]

async def create_temperature_series(temperature_series: Optional[float] = None) -> TemperatureSeries:
    if isinstance(temperature_series, float):
        return TemperatureSeries(
            value=np.array(temperature_series, dtype=np.float32),
            unit=SYMBOL_UNIT_TEMPERATURE)
    
    return TemperatureSeries(
        value=np.array(TEMPERATURE_DEFAULT, dtype=np.float32),
        unit=SYMBOL_UNIT_TEMPERATURE)


async def create_wind_speed_series(wind_speed_series: Optional[float] = None) -> WindSpeedSeries:
    
    if isinstance(wind_speed_series, float):
        return WindSpeedSeries(
            value=np.array(wind_speed_series),
            unit=SYMBOL_UNIT_WIND_SPEED)
    
    return WindSpeedSeries(
        value=np.array(WIND_SPEED_DEFAULT),
        unit=SYMBOL_UNIT_WIND_SPEED)


async def create_spectral_factor_series(spectral_factor_series: float | None = None) -> SpectralFactorSeries:
    
    if isinstance(spectral_factor_series, float):
        return SpectralFactorSeries(
            value=np.array(spectral_factor_series, dtype=np.float32)
            )
    
    return SpectralFactorSeries(
        value=np.array(SPECTRAL_FACTOR_DEFAULT, dtype=np.float32)
        )


async def process_linke_turbidity_factor(
        linke_turbidity_factor: Annotated[float, fastapi_query_linke_turbidity_factor_series] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
) -> LinkeTurbidityFactor:
    return LinkeTurbidityFactor(value = linke_turbidity_factor)


async def process_angle_output_units(
        angle_output_units: Annotated[AngleOutputUnit, fastapi_query_angle_output_units] = AngleOutputUnit.RADIANS
)-> str:
    if angle_output_units.value == AngleOutputUnit.RADIANS.value:
        return RADIANS
    else:
        return DEGREES


async def process_refracted_solar_zenith(
        refracted_solar_zenith: Annotated[float, fastapi_query_refracted_solar_zenith] =  math.degrees(REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT)
)->float:
    return math.radians(refracted_solar_zenith)


async def process_surface_tilt_list(
        surface_tilt: Annotated[list[float], fastapi_query_surface_tilt_list] = [float(SURFACE_TILT_DEFAULT)],
        surface_orientation: Annotated[list[float], fastapi_query_surface_orientation_list] = [float(SURFACE_ORIENTATION_DEFAULT)]
)->list[float]:
    for surface_tilt_value in surface_tilt:
        if not SURFACE_TILT_MINIMUM <= surface_tilt_value <= SURFACE_TILT_MAXIMUM:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Value {surface_tilt_value} is out of the range {SURFACE_TILT_MINIMUM}-{SURFACE_TILT_MAXIMUM}.")
    
    if len(surface_orientation) != len(surface_tilt):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Surface tilt options and surface orientation options must have the same number of inputs")
    
    return [math.radians(surface_tilt_value) for surface_tilt_value in surface_tilt]


async def process_surface_orientation_list(
        surface_tilt: Annotated[list[float], fastapi_query_surface_tilt_list] = [float(SURFACE_TILT_DEFAULT)],
        surface_orientation: Annotated[list[float], fastapi_query_surface_orientation_list] = [float(SURFACE_ORIENTATION_DEFAULT)]
)->list[float]:
    for surface_orientation_value in surface_orientation:
        if not SURFACE_ORIENTATION_MINIMUM <= surface_orientation_value <= SURFACE_ORIENTATION_MAXIMUM:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Value {surface_orientation_value} is out of the range {SURFACE_ORIENTATION_MINIMUM}-{SURFACE_ORIENTATION_MAXIMUM}.")
    
    if len(surface_orientation) != len(surface_tilt):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Surface tilt options and surface orientation options must have the same number of inputs")
    
    return [math.radians(surface_orientation_value) for surface_orientation_value in surface_orientation]


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
fastapi_dependable_linke_turbidity_factor = Depends(process_linke_turbidity_factor)
fastapi_dependable_angle_output_units = Depends(process_angle_output_units)
fastapi_dependable_refracted_solar_zenith = Depends(process_refracted_solar_zenith)
fastapi_dependable_surface_orientation_list = Depends(process_surface_orientation_list)
fastapi_dependable_surface_tilt_list = Depends(process_surface_tilt_list)
