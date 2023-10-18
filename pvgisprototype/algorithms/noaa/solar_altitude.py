from devtools import debug
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarAltitudeNOAAInput
from pvgisprototype.validation.functions import CalculateSolarAltitudeNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarAltitudeTimeSeriesNOAAInput
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from datetime import datetime
from typing import Union
from typing import Sequence
from zoneinfo import ZoneInfo
from datetime import datetime
from typing import Union
from typing import Sequence
from zoneinfo import ZoneInfo
from pvgisprototype import SolarAltitude
from pvgisprototype.constants import RADIANS
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_noaa
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa
from math import pi
from math import isfinite
import numpy as np
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_noaa
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa
from math import pi
from math import isfinite
import numpy as np


@validate_with_pydantic(CalculateSolarAltitudeNOAAInput)
def calculate_solar_altitude_noaa(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    apply_atmospheric_refraction: bool = True,
    verbose: int = 0,
)-> SolarAltitude:
    """Calculate the solar altitude angle for a location and moment in time"""
    solar_hour_angle = calculate_solar_hour_angle_noaa(
        longitude=longitude,
        timestamp=timestamp,
        timezone=timezone,
    )
    solar_zenith = calculate_solar_zenith_noaa(
        latitude=latitude,
        timestamp=timestamp,
        solar_hour_angle=solar_hour_angle,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    solar_altitude = pi / 2 - solar_zenith.radians
    solar_altitude = SolarAltitude(
        value=solar_altitude,
        unit=RADIANS,
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
        )
    if (
        not isfinite(solar_altitude.degrees)
        or not solar_altitude.min_degrees <= solar_altitude.degrees <= solar_altitude.max_degrees
    ):
        raise ValueError(
            f"The calculated solar altitude angle {solar_altitude.degrees} is out of the expected range\
            [{solar_altitude.min_degrees}, {solar_altitude.max_degrees}] radians"
        )
    if verbose == 3:
        debug(locals())
    if (
        not isfinite(solar_altitude.degrees)
        or not solar_altitude.min_degrees <= solar_altitude.degrees <= solar_altitude.max_degrees
    ):
        raise ValueError(
            f"The calculated solar altitude angle {solar_altitude.degrees} is out of the expected range\
            [{solar_altitude.min_degrees}, {solar_altitude.max_degrees}] radians"
        )
    if verbose == 3:
        debug(locals())

    return solar_altitude


@validate_with_pydantic(CalculateSolarAltitudeTimeSeriesNOAAInput)
def calculate_solar_altitude_time_series_noaa(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: Union[float, Sequence[float]],
    timezone: ZoneInfo,
    apply_atmospheric_refraction: bool = True,
    verbose: int = 0,
):
    """Calculate the solar altitude angle for a location over a time series"""
    """Calculate the solar altitude angle for a location over a time series"""
    solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
        longitude,
        timestamps,
        timezone,
    )
    solar_zenith_series = calculate_solar_zenith_time_series_noaa(
        latitude=latitude,
        timestamps=timestamps,
        solar_hour_angle_series=solar_hour_angle_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
    )
    solar_altitude_series = np.pi / 2 - np.array(
        [zenith.radians for zenith in solar_zenith_series]
    )
    if not np.all(np.isfinite(solar_altitude_series)) or not np.all(
        (-np.pi / 2 <= solar_altitude_series) & (solar_altitude_series <= np.pi / 2)
    ):
        raise ValueError(
            f"The `solar_altitude` should be a finite number ranging in [{-np.pi/2}, {np.pi/2}] radians"
        )
    solar_altitude_series = [
        SolarAltitude(value=altitude, unit=RADIANS) for altitude in solar_altitude_series
    ]
    if verbose == 3:
        debug(locals())

    return np.array(solar_altitude_series, dtype=object)
