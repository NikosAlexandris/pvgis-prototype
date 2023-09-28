import typer
from typing import Annotated
from typing import Union
from typing import Sequence
from typing import List
from typing import Optional
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from math import sin, cos, acos
from math import asin
from math import atan
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_noaa
from pvgisprototype.api.geometry.solar_declination import calculate_solar_declination_pvis
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.api.utilities.conversions import convert_to_radians
from pvgisprototype.api.utilities.timestamp import ctx_attach_requested_timezone

from pvgisprototype import RelativeLongitude
from pvgisprototype import SolarIncidence
from pvgisprototype import HorizonHeight
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarHourAngle

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateRelativeLongitudeInputModel
from pvgisprototype.validation.functions import CalculateSolarIncidenceJencoInputModel
from pvgisprototype.validation.functions import CalculateSolarIncidenceTimeSeriesJencoInputModel
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import HORIZON_HEIGHT_UNIT
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import NO_SOLAR_INCIDENCE
from pvgisprototype.constants import RADIANS
import numpy as np


@validate_with_pydantic(CalculateRelativeLongitudeInputModel)
def calculate_relative_longitude(
    latitude: Latitude,
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    surface_orientation: float = SURFACE_ORIENTATION_DEFAULT,
    angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
) -> RelativeLongitude:
    """
    Notes
    -----
    Hofierka, 2002 uses equations presented by Jenco :
    tangent_relative_longitude =
                                - sin(surface_tilt)
                                * sin(surface_orientation) /
                                  sin(latitude) 
                                * sin(surface_tilt) 
                                * cos(surface_orientation) 
                                + cos(latitude) 
                                * cos(surface_tilt)

    In PVGIS' C source code :

    There is an error of one negative sign in either of the expressions! That
    is so because : cos(pi/2 + x) = -sin(x).

    tangent_relative_longitude =

            - cos(half_pi - surface_tilt)           # cos(pi/2 - x) = sin(x)
    
            * cos(half_pi + surface_orientation) /  # cos(pi/2 + x) = -sin(x)
            
            sin(latitude) 
            
            * cos(half_pi - surface_tilt) 
            
            * sin(half_pi + surface_orientation)    # sin(pi/2 + x) = cos(x)
            
            + cos(latitude) 
            
            * sin(half_pi - surface_tilt)           # sin(pi/2 - x) = cos(x)
    """
    tangent_relative_longitude_numerator = -(
        sin(surface_tilt.radians)
        * sin(surface_orientation.radians)
    )
    tangent_relative_longitude_denominator = (
            sin(latitude.radians)
        * sin(surface_tilt.radians)
        * cos(surface_orientation.radians)
        + cos(latitude.radians)
        * cos(surface_tilt.radians)
    )
    tangent_relative_longitude = (
        tangent_relative_longitude_numerator /
        tangent_relative_longitude_denominator
    )
    relative_longitude = atan(tangent_relative_longitude)
    relative_longitude = RelativeLongitude(
        value=relative_longitude,
        unit=angle_output_units,
    )
    return relative_longitude


@validate_with_pydantic(CalculateSolarIncidenceJencoInputModel)
def calculate_solar_incidence_jenco(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo = None,
    random_time: bool = False,
    # hour_angle: SolarHourAngle = None,
    surface_tilt: float = None,
    surface_orientation: float = None,
    shadow_indicator: Path = None,
    horizon_heights: Optional[List[float]] = None,
    horizon_interval: Optional[float] = None,
    days_in_a_year: float = DAYS_IN_A_YEAR,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: str = TIME_OUTPUT_UNITS_DEFAULT,
    angle_units: str = 'radians',
    angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> SolarIncidence:
    """Calculate the solar incidence based on sun's position and surface geometry.

    Parameters
    ----------
    hour_angle : float
        The solar hour angle in radians.
    longitude : float
        Longitude in degrees
    latitude : float
        Latitude in degrees
    surface_tilt : float
        Tilt of the surface in degrees
    surface_orientation : float
        Orientation of the surface (azimuth angle in degrees)
    # shadow_indicator : int, optional
    #     Shadow data indicating presence of shadow, by default None.
    # horizon_heights : list of float, optional
    #     List of horizon height values, by default None.
    # horizon_interval : float, optional
    #     Interval between successive horizon data points, by default None.

    Returns
    -------
    float
        Solar incidence angle.
        # Solar incidence angle or NO_SOLAR_INCIDENCE if a shadow is detected.

    Notes
    -----

    tg(λ') = - (sin(γN) * sin(AN)) / (sin(ϕ) * sin(γN) * cos(AN) + cos(ϕ) * cos(γN))
    sin(ϕ') = - cos(ϕ) * sin(γN) * cos(AN) + sin(ϕ) * cos(γN)
    C'31 = cos ϕ' cos δ
    C'33 = sin ϕ' sin δ


    From PVGIS' C++ source code:
    
    The `timeAngle` (which is the solar hour
    angle) in `rsun_standalone_hourly_opt.cpp` is calculated via:

        `sunGeom->timeAngle = (solarTimeOfDay - 12) * HOURANGLE;`

    where HOUR_ANGLE is defined as `HOUR_ANGLE = pi / 12.0`
    which is the conversion factor to radians (π/2 = 0.261799)
    and hence this is the equation to calculate the hour angle
    e.g., as per NOAA's equation:
        
        `solar_hour_angle = (true_solar_time - 720) * (pi / 720)`.

    in which 720 is minutes, whereas 60 is hours in PVGIS' C++ code.

    """
    # solar_altitude = calculate_solar_altitude()
    solar_altitude = None
    # solar_azimuth = calculate_solar_azimuth()
    solar_azimuth = None
    in_shade = is_surface_in_shade(
            solar_altitude=solar_altitude,
            solar_azimuth=solar_azimuth,
            shadow_indicator=shadow_indicator,
            horizon_heights=horizon_heights,
            horizon_interval=horizon_interval,
    )
    if in_shade:
        return NO_SOLAR_INCIDENCE

    else:
        sine_relative_inclined_latitude = - (
            cos(latitude.radians)
            * sin(surface_tilt.radians)
            * cos(surface_orientation.radians)
            + sin(latitude.radians)
            * cos(surface_tilt.radians)
        )
        relative_inclined_latitude = asin(sine_relative_inclined_latitude)
        solar_declination = calculate_solar_declination_pvis(
            timestamp=timestamp,
            timezone=timezone,
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
        )
        c_inclined_31 = cos(relative_inclined_latitude) * cos(solar_declination.radians)
        c_inclined_33 = sine_relative_inclined_latitude * sin(solar_declination.radians)
        solar_hour_angle = calculate_solar_hour_angle_noaa(
            longitude=longitude,
            timestamp=timestamp,
            timezone=timezone,
            time_output_units=time_output_units,
            angle_output_units=angle_output_units,
        )
        relative_longitude = calculate_relative_longitude(
            latitude=latitude,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation
        )
        sine_solar_incidence = (
            c_inclined_31 * cos(solar_hour_angle.radians - relative_longitude.radians) + c_inclined_33
        )
        solar_incidence = SolarIncidence(
            value=asin(sine_solar_incidence),
            unit=RADIANS,
        )

    # return max(NO_SOLAR_INCIDENCE, solar_incidence)
    return solar_incidence


@validate_with_pydantic(CalculateSolarIncidenceTimeSeriesJencoInputModel)
def calculate_solar_incidence_time_series_jenco(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: np.array,
    timezone: Optional[ZoneInfo] = None,
    random_time_series: bool = RANDOM_DAY_SERIES_FLAG_DEFAULT,
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    surface_orientation: float = SURFACE_ORIENTATION_DEFAULT,
    days_in_a_year: float = DAYS_IN_A_YEAR,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: str = TIME_OUTPUT_UNITS_DEFAULT,
    angle_units: str = 'radians',
    angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> np.array:
    solar_incidence_angle_series = np.empty_like(timestamps, dtype=float)

    solar_declination_series = calculate_solar_declination_time_series_noaa(
        timestamps=timestamps,
        angle_output_units=angle_output_units,
    )
    solar_declination_series = np.array([item.radians for item in solar_declination_series])
    sine_relative_inclined_latitude = -(
        cos(latitude.radians) * sin(surface_tilt) * cos(surface_orientation)
        + sin(latitude.radians) * cos(surface_tilt)
    )
    relative_inclined_latitude = np.arcsin(sine_relative_inclined_latitude)
    c_inclined_31_series = cos(relative_inclined_latitude) * np.cos(
        solar_declination_series
    )
    c_inclined_33_series = sine_relative_inclined_latitude * np.sin(
        solar_declination_series
    )
    solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        time_output_units=time_output_units,
        angle_output_units=angle_output_units,
    )
    solar_hour_angle_series = np.array([item.radians for item in solar_hour_angle_series])
    relative_longitude = calculate_relative_longitude(
        latitude, surface_tilt, surface_orientation
    )
    sine_solar_incidence_series = (
        c_inclined_31_series * np.cos(solar_hour_angle_series - relative_longitude.radians)
        + c_inclined_33_series
    )
    solar_incidence_angle_series = np.arcsin(sine_solar_incidence_series)

    return solar_incidence_angle_series


# @validate_with_pydantic()
def interpolate_horizon_height(
    solar_azimuth: float,
    horizon_heights: List[float],
    horizon_interval: float,
) -> HorizonHeight:
    """Interpolate the height of the horizon at the sun's azimuth angle.

    Parameters
    ----------
    solar_azimuth : float
        The azimuth angle of the sun.
    horizon_heights : list of float
        List of horizon height values.
    horizon_interval : float
        Interval between successive horizon data points.

    Returns
    -------
    float
        The interpolated horizon height.
    """
    position_in_interval = solar_azimuth / horizon_interval
    position_before = int(position_in_interval)
    position_after = position_before + 1

    # Handle wrap around
    position_after = 0 if position_after == len(horizon_heights) else position_after

    # Interpolate the horizon height (or weighted average)
    horizon_height = (
        (1 - (position_in_interval - position_before))
        * horizon_heights[position_before] 
        + (position_in_interval - position_before)
        * horizon_heights[position_after]
    )

    return HorizonHeight(horizon_height, HORIZON_HEIGHT_UNIT)


def is_surface_in_shade(
    solar_altitude: float,
    solar_azimuth: float,
    shadow_indicator: Path = None,
    horizon_heights: Optional[List[float]] = None,
    horizon_interval: Optional[float] = None,
) -> bool:
    """Check whether the solar surface is in shade based on shadow and horizon data.

    Parameters
    ----------
    shadow_indicator : int, optional
        Shadow data indicating presence of shadow, by default None.
    solar_altitude : float
        The altitude of the sun.
    solar_azimuth : float
        The azimuth angle of the sun.
    horizon_heights : list of float, optional
        List of horizon height values, by default None.
    horizon_interval : float, optional
        Interval between successive horizon data points, by default None.

    Returns
    -------
    bool
        True if the solar surface is in shade, otherwise False.
    """
    if shadow_indicator is not None and bool(shadow_indicator):
        return True

    if horizon_heights is not None:
        horizon_height = interpolate_horizon_height(solar_azimuth, horizon_heights, horizon_interval)
        if horizon_height > solar_altitude:
            return True
    
    return False
