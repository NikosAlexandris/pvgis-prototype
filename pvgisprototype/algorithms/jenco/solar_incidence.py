from devtools import debug
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
from pvgisprototype.api.geometry.declination import calculate_solar_declination_pvis
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

from pvgisprototype import SurfaceTilt
from pvgisprototype import SurfaceOrientation
from pvgisprototype import SolarHourAngle

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateRelativeLongitudeInputModel
from pvgisprototype.validation.functions import CalculateSolarIncidenceJencoInputModel
from pvgisprototype.validation.functions import CalculateSolarIncidenceTimeSeriesJencoInputModel
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import HORIZON_HEIGHT_UNIT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import NO_SOLAR_INCIDENCE
from pvgisprototype.constants import RADIANS
import numpy as np
from pvgisprototype.api.irradiance.shade import is_surface_in_shade


@validate_with_pydantic(CalculateRelativeLongitudeInputModel)
def calculate_relative_longitude(
    latitude: Latitude,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
) -> RelativeLongitude:
    """
    Notes
    -----
    Hofierka, 2002 uses equations presented by Jenco :

        tangent_relative_longitude =
                                    (
                                        - sin(surface_tilt)
                                        * sin(surface_orientation)
                                    ) / (
                                        sin(latitude)
                                        * sin(surface_tilt)
                                        * cos(surface_orientation)
                                        + cos(latitude)
                                        * cos(surface_tilt)
                                    )

    In PVGIS' C source code, there is an error of one negative sign in either
    of the expressions! That is so because : cos(pi/2 + x) = -sin(x).

        tangent_relative_longitude =
            (
              - cos(half_pi - surface_tilt)           # cos(pi/2 - x) = sin(x)
              * cos(half_pi + surface_orientation)    # cos(pi/2 + x) = -sin(x)
            ) / (
              sin(latitude) 
              * cos(half_pi - surface_tilt) 
              * sin(half_pi + surface_orientation)    # sin(pi/2 + x) = cos(x)
              + cos(latitude) 
              * sin(half_pi - surface_tilt)           # sin(pi/2 - x) = cos(x)
            )
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
        unit=RADIANS,
    )
    return relative_longitude


@validate_with_pydantic(CalculateSolarIncidenceJencoInputModel)
def calculate_solar_incidence_jenco(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo = None,
    surface_tilt: SurfaceTilt = None,
    surface_orientation: SurfaceOrientation = None,
    shadow_indicator: Path = None,
    horizon_heights: Optional[List[float]] = None,
    horizon_interval: Optional[float] = None,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> SolarIncidence:
    """Calculate the solar incidence angle based on the position of the sun and
    the inclination angle of a surface.

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

    An inclined surface is defined by the inclination angle (also known as
    slope or tilt) `γN` and the azimuth (also known as aspect or orientation)
    `AN`. The latter is the angle between the projection of the normal on the
    horizontal surface and East.

    tg(λ') = - (sin(γN) * sin(AN)) / (sin(ϕ) * sin(γN) * cos(AN) + cos(ϕ) * cos(γN))
    sin(ϕ') = - cos(ϕ) * sin(γN) * cos(AN) + sin(ϕ) * cos(γN)
    C'31 = cos ϕ' cos δ
    C'33 = sin ϕ' sin δ


    From PVGIS' C++ source code:
    
    The `timeAngle` (which is the solar hour
    angle) in `rsun_standalone_hourly_opt.cpp` is calculated via:

        `sunGeom->timeAngle = (solarTimeOfDay - 12) * HOURANGLE;`

    where HOUR_ANGLE is defined as `HOUR_ANGLE = pi / 12.0`
    which is the conversion factor to radians (π / 12 = 0.261799)
    and hence this is the equation to calculate the hour angle
    e.g., as per NOAA's equation:
        
        `solar_hour_angle = (true_solar_time - 720) * (pi / 720)`.

    in which 720 is minutes, whereas 60 is hours in PVGIS' C++ code.
    """
    solar_altitude = None
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
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
        )
        c_inclined_31 = cos(relative_inclined_latitude) * cos(solar_declination.radians)
        c_inclined_33 = sin(relative_inclined_latitude) * sin(solar_declination.radians)
        solar_hour_angle = calculate_solar_hour_angle_noaa(
            longitude=longitude,
            timestamp=timestamp,
            timezone=timezone,
        )
        relative_longitude = calculate_relative_longitude(
            latitude=latitude,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation
        )
        sine_solar_incidence = (
            c_inclined_31 * cos(solar_hour_angle.radians - relative_longitude.radians)
            + c_inclined_33
        )
        solar_incidence = asin(sine_solar_incidence)

    if solar_incidence < 0:
        solar_incidence = NO_SOLAR_INCIDENCE

    return SolarIncidence(value=solar_incidence, unit=RADIANS)


@validate_with_pydantic(CalculateSolarIncidenceTimeSeriesJencoInputModel)
def calculate_solar_incidence_time_series_jenco(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: np.array,
    timezone: Optional[ZoneInfo] = None,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    time_output_units: str = TIME_OUTPUT_UNITS_DEFAULT,
    angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> SolarIncidence:
    """Calculate the solar incidence angle based on the position of the sun and
    the inclination angle of a surface over a period of time

    Parameters
    ----------
    longitude : float
        Longitude in degrees
    latitude : float
        Latitude in degrees
    surface_tilt : float
        Tilt of the surface in degrees
    surface_orientation : float
        Orientation of the surface (azimuth angle in degrees)

    Returns
    -------
    ndarray
        Solar incidence angle or NO_SOLAR_INCIDENCE series if a shadow is detected.
    """
    sine_relative_inclined_latitude = -(
        cos(latitude.radians) * sin(surface_tilt.radians) * cos(surface_orientation.radians)
        + sin(latitude.radians) * cos(surface_tilt.radians)
    )
    relative_inclined_latitude = np.arcsin(sine_relative_inclined_latitude)
    solar_declination_series = calculate_solar_declination_time_series_noaa(
        timestamps=timestamps,
        angle_output_units=angle_output_units,
    )
    c_inclined_31_series = cos(relative_inclined_latitude) * np.cos(
        solar_declination_series.radians
    )
    c_inclined_33_series = sin(relative_inclined_latitude) * np.sin(
        solar_declination_series.radians
    )
    solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        time_output_units=time_output_units,
        angle_output_units=angle_output_units,
    )
    relative_longitude = calculate_relative_longitude(
        latitude=latitude,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
    )
    sine_solar_incidence_series = (
        c_inclined_31_series * np.cos(solar_hour_angle_series.radians - relative_longitude.radians)
        + c_inclined_33_series
    )
    solar_incidence_series = np.arcsin(sine_solar_incidence_series)
    solar_incidence_series[solar_incidence_series < 0] = NO_SOLAR_INCIDENCE

    solar_incidence_series = SolarIncidence(
        value=solar_incidence_series,
        unit=RADIANS,
        position_algorithm='Jenco',
        timing_algorithm='Jenco',
    )

    if verbose > 5:
        debug(locals())

    return solar_incidence_series
