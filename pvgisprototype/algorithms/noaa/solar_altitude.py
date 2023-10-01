from devtools import debug
from typing import Union
from typing import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from math import pi
from math import isfinite
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarAltitudeNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarAltitudeTimeSeriesNOAAInput
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarHourAngle
from pvgisprototype import SolarZenith
from pvgisprototype import SolarAltitude
from pvgisprototype.constants import RADIANS
from .solar_hour_angle import calculate_solar_hour_angle_noaa
from .solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from .solar_zenith import calculate_solar_zenith_noaa
from .solar_zenith import calculate_solar_zenith_time_series_noaa


@validate_with_pydantic(CalculateSolarAltitudeNOAAInput)
def calculate_solar_altitude_noaa(
        longitude: Longitude,   # radians
        latitude: Latitude,     # radians
        timestamp: datetime,
        timezone: ZoneInfo,
        apply_atmospheric_refraction: bool = True,
        time_output_units: str = 'minutes',
        # angle_output_units: str = 'radians',
    )-> SolarAltitude:
    """Calculate the solar zenith angle (φ) in radians
    """
    solar_hour_angle = calculate_solar_hour_angle_noaa(
        longitude=longitude,
        timestamp=timestamp,
        timezone=timezone,
        time_output_units=time_output_units,
        # angle_output_units='radians',
    )
    solar_zenith = calculate_solar_zenith_noaa(
        latitude=latitude,
        timestamp=timestamp,
        solar_hour_angle=solar_hour_angle,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        # angle_output_units='radians',
    )
    solar_altitude = pi/2 - solar_zenith.radians
    if (
        not isfinite(solar_altitude.radians)
        or not -pi / 2 <= solar_altitude.radians <= pi / 2
    ):
        raise ValueError(
            f"The `solar_altitude` should be a finite number ranging in [{-pi/2}, {pi/2}] radians"
        )
    solar_altitude = SolarAltitude(value=solar_altitude, unit=RADIANS)

    if not isfinite(solar_altitude.radians) or not -pi/2 <= solar_altitude.radians <= pi/2:
        raise ValueError(f'The `solar_altitude` should be a finite number ranging in [{-pi/2}, {pi/2}] radians')

    return solar_altitude


@validate_with_pydantic(CalculateSolarAltitudeTimeSeriesNOAAInput)
def calculate_solar_altitude_time_series_noaa(
    longitude: Longitude,  # radians
    latitude: Latitude,  # radians
    timestamps: Union[float, Sequence[float]],
    timezone: str,
    apply_atmospheric_refraction: bool = True,
    time_output_units: str = "minutes",
    angle_output_units: str = "radians",
    verbose: int = 0,
):
    """Calculate the solar zenith angle (φ) in radians for a time series"""
    solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
        longitude,
        timestamps,
        timezone,
        time_output_units,
        angle_output_units,
    )
    solar_zenith_series = calculate_solar_zenith_time_series_noaa(
        latitude=latitude,
        timestamps=timestamps,
        solar_hour_angle_series=solar_hour_angle_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        angle_output_units="radians",
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
        SolarAltitude(value=value, unit="radians") for value in solar_altitude_series
    ]
    solar_altitude_series = [
        convert_to_degrees_if_requested(altitude, angle_output_units)
        for altitude in solar_altitude_series
    ]

    if verbose == 3:
        debug(locals())
    return np.array(solar_altitude_series, dtype=object)
