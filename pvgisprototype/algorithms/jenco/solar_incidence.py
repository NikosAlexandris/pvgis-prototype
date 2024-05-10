from devtools import debug
from typing import List
from typing import Optional
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from math import pi, sin, cos, acos, asin, atan
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_noaa
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_noaa
from pvgisprototype.algorithms.noaa.solar_altitude import calculate_solar_altitude_noaa
from pvgisprototype.algorithms.jenco.solar_altitude import calculate_solar_altitude_time_series_jenco
from pvgisprototype.algorithms.jenco.solar_azimuth import calculate_solar_azimuth_time_series_jenco
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
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
from pvgisprototype.api.position.models import SolarIncidenceModel

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateRelativeLongitudeInputModel
from pvgisprototype.validation.functions import CalculateSolarIncidenceJencoInputModel
from pvgisprototype.validation.functions import CalculateSolarIncidenceTimeSeriesJencoInputModel
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import HORIZON_HEIGHT_UNIT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import NO_SOLAR_INCIDENCE
from pvgisprototype.constants import RADIANS
import numpy as np
from pvgisprototype.api.irradiance.shade import is_surface_in_shade
from pvgisprototype.api.irradiance.shade import is_surface_in_shade_time_series
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pandas import DatetimeIndex


@log_function_call
@validate_with_pydantic(CalculateRelativeLongitudeInputModel)
def calculate_relative_longitude(
    latitude: Latitude,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
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
    As a consequence, the numerator becomes a positive number.

        Source code :

        /* These calculations depend on slope and aspect. Constant for the day if not tracking */
        sin_phi_l = -gridGeom->coslat * cos_u * sin_v + gridGeom->sinlat * sin_u;
        latid_l = asin(sin_phi_l);
        cos_latid_l = cos(latid_l);
        q1 = gridGeom->sinlat * cos_u * sin_v + gridGeom->coslat * sin_u;
        tan_lam_l = - cos_u * cos_v / q1;
        longit_l = atan (tan_lam_l);
        if((aspect<M_PI)&&(longit_l<0.))
        {
            longit_l += M_PI;
        }				
        else if((aspect>M_PI)&&(longit_l>0.))
        {
            longit_l -= M_PI;
        }				


        Translation in to Python / pseudocode :

        tangent_relative_longitude =
            (
              - cos(half_pi - surface_tilt)         # cos(pi/2 - x) = sin(x)
              * cos(half_pi + surface_orientation)  # cos(pi/2 + x) = -sin(x) #
            ) / (
              sin(latitude) 
              * cos(half_pi - surface_tilt) 
              * sin(half_pi + surface_orientation)  # sin(pi/2 + x) = cos(x)
              + cos(latitude) 
              * sin(half_pi - surface_tilt)         # sin(pi/2 - x) = cos(x)
            )

    As a consequence, PVGIS is like (note the positive numerator!) : 

        tangent_relative_longitude =
            (
                sin(surface_tilt)
                * sin(surface_orientation)
            ) / (
                sin(latitude)
                * sin(surface_tilt)
                * cos(surface_orientation)
                + cos(latitude)
                * cos(surface_tilt)
            )
    """
    # -----------------------------------------------------------------------
    # in PVGIS an extra minus sign results to an all positive numerator!
    # tangent_relative_longitude_numerator = sin(surface_tilt.radians) * sin(
    #     surface_orientation.radians
    # )
    # -----------------------------------------------------------------------
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
    # force dtype !
    relative_longitude = np.array(
        [tangent_relative_longitude_numerator / tangent_relative_longitude_denominator],
        dtype=dtype,
    )
    log_data_fingerprint(
            data=relative_longitude,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return RelativeLongitude(
        value=relative_longitude,
        unit=RADIANS,
    )


@validate_with_pydantic(CalculateSolarIncidenceJencoInputModel)
def calculate_solar_incidence_jenco(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo = None,
    surface_orientation: SurfaceOrientation = None,
    surface_tilt: SurfaceTilt = None,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    shadow_indicator: Path = None,
    horizon_heights: Optional[List[float]] = None,
    horizon_interval: Optional[float] = None,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarIncidence:
    """Calculate the solar incidence angle 

    Calculate the solar incidence angle between the direction of the sun
    rays and the inclination angle of a reference surface. Alternatively the
    function can return the angle between the sun-vector and the normal vector
    to the reference surface.

    Parameters
    ----------
    hour_angle : float
        The solar hour angle in radians.
    longitude : float
        Longitude in degrees
    latitude : float
        Latitude in degrees
    surface_orientation : float
        Orientation of the surface (azimuth angle in degrees)
    surface_tilt : float
        Tilt of the surface in degrees
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
    The solar incidence angle is the single most important quantity in the
    solar geometry setup. Its definition will affect all subsequent operations
    excluding none of the irradiance components, nor the photovoltaic power or
    energy estimations.

    Attention! There is no one, and only one, definition of the solar incidence
    angle! While many authors refer to the angle between the sun-vector and the
    normal to the reference surface, for example Martin and Ruiz (2002, 2005),
    others, like for example Jenco (1992) and Hofierka (2002), consider as
    incidence the angle between the sun-vector and the reference surface-plane.
    These angles are complementary to each other. This fact is an important one
    when treating trigonometric relationships that affect the calculation of
    the incidence angle.

    In this program, we implement and consider as _complementary_ the incidence
    angle as defined by Jenco (1992) between the direction of the sun-rays and
    the inclination angle, or plane, of a reference surface. Hence, the default
    modus of this function returns the _complementary_ incidence angle.

    Following is meant to visualise a flat horizontal surface and the
    direction of a sun-ray. The angle between the two is what we call
    complementary.

          \
           \
        ____\

    Optionally, the function can return the _typical_ incidence angle between
    the direction of the sun-rays and the normal direction to the reference
    surface in question.

    Following means to visualise the same direction of a sun-ray and then the
    normal (vertical here) direction to the flat horizontal surface. The angle
    between the sun-ray and the normal (vertical here) direction is the
    _typical_ definition of the solar incidence angle. This angle can be
    generated via the `complementary_incidence_angle` flag.

         \  |
          \ |
           \|
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
    and hence this is the equation to calculate the hour angle in radians,
    e.g., as per NOAA's equation:
        
        `solar_hour_angle = (true_solar_time - 720) * (pi / 720)`.

    in which 720 is minutes, whereas 60 is hours in PVGIS' C++ code.
    """
    # Would it make sense to offer other _altitude algorithms_ ? -------------
    solar_altitude = calculate_solar_altitude_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            # solar_position_models=solar_position_model,
            # solar_time_model=solar_time_model,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            # perigee_offset=perigee_offset,
            # eccentricity_correction_factor=eccentricity_correction_factor,
            # angle_output_units=angle_output_units,
            verbose=0,
            )
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
        solar_declination = calculate_solar_declination_noaa(
            timestamp=timestamp,
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
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
        )
        sine_solar_incidence = (
            c_inclined_31 * cos(solar_hour_angle.radians - relative_longitude.radians)
            + c_inclined_33
        )
        solar_incidence = asin(sine_solar_incidence)

    description = "The 'complementary' incidence angle between the position of the sun (sun-vector) and the inclination of a surface (surface-plane)."
    if not complementary_incidence_angle:  # derive the 'typical' incidence angle
        logger.info(':information: [bold][magenta]Converting[/magenta] solar incidence angle to Sun-to-Surface-Normal[/bold]...')
        solar_incidence = (pi / 2) - solar_incidence
        description='Incidence angle between sun-vector and surface-normal'

    if solar_incidence < 0:
        solar_incidence = NO_SOLAR_INCIDENCE

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return SolarIncidence(
        value=solar_incidence,
        unit=RADIANS,
        positioning_algorithm=solar_altitude.position_algorithm,  #
        timing_algorithm=solar_hour_angle.timing_algorithm,  #
        incidence_algorithm=SolarIncidenceModel.jenco,
        description=description,
    )


@log_function_call
@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateSolarIncidenceTimeSeriesJencoInputModel)
def calculate_solar_incidence_time_series_jenco(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: Optional[ZoneInfo] = None,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    shadow_indicator: Path = None,
    horizon_heights: Optional[List[float]] = None,
    horizon_interval: Optional[float] = None,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
) -> SolarIncidence:
    """Calculate the solar incidence angle between the position of the sun and
    the inclination plane of a surface.

    Calculate the solar incidence angle based on the position of the sun
    (sun-vector) and the inclination angle of a surface (surface-plane)
    over a period of time. We call this the "complementary" incidence angle
    contrasting typical definitions of the incidence angle between the
    sun-vector and the normal to the surface in question.

    Parameters
    ----------
    longitude : float
        Longitude in degrees
    latitude : float
        Latitude in degrees
    surface_orientation : float
        Orientation of the surface (azimuth angle in degrees)
    surface_tilt : float
        Tilt of the surface in degrees

    Returns
    -------
    ndarray
        Solar incidence angle or NO_SOLAR_INCIDENCE series if a shadow is detected.

    Notes
    -----
    Reading from the original paper (last page is a summary translation in
    English):

        Orientation of georelief An with respect to Cardinal points and slopes
        γN of georelief in the direction of slope curves in the given point on
        the georelief with the latitude φ determines the latitude φ' and in
        relation to longitude λ of this point also the relative longitude λ' of
        the contact point of contact plane to reference spheric surface of the
        Earth with identical course of the insolation (Fig. 1). Thus sinus of
        insolation angle δexp on georelief for the local time moment T can be
        expressed by modification of a relation that is well known in astronomy
        for the calculation of sinus of solar altitude h0 a form of equation
        (3). Latitude φ' and longitude λ' in the equation (3) is definitely
        determined on the basis of transformation equations (4.3.31) in the
        work [5] in dependence on the assessment of the basic direction of
        orientation of georelief AN with respect to the cardinal points by
        goniometric equations (5), (6) or (9), (10). After determination of the
        hour of sunrise (Tv)s from shadow to light and hour of sunset (Tr)s
        from light to shadow by equations (12), (13) abstracting also from hill
        shading of georelief, total quantity of direct solar irradiance Qd on
        the unit of area of georelief for one day under blue sky conditions can
        be expressed by equation (14).

    Although Hofierka (2002) does not explicitly state "the angle between the
    sun-vector and the plane to the surface," he borrows the equation defined
    by Jenco (1992) who measures the incidence angle between the sun-vector and
    plane of the reference solar surface. Care needs to be taken when comparing
    or using other definitions of the solar incidence angle.

    - Shadow check not implemented.
    - In PVGIS' source code, in order :

      1. positive numerator for the relative_longitude -- which is an error
      
      2. following adjustments -- unsure what they mean to achieve -- are
         placed befor calculating the incidence angle :

          if surface_orientation.radians < pi and relative_longitude.value < 0:
              relative_longitude += pi
          if surface_orientation.radians > pi and relative_longitude.value > 0:
              relative_longitude -= pi

        Here a ready-to-use snippet in Python:

        ``` py
        from rich import print
        print(f'Surface orientation  : {surface_orientation}')
        print(f'Relative longitude : {relative_longitude}')
        if surface_orientation.radians < np.pi and relative_longitude.value < 0:
            print(f'[bold red]Add[/bold red] {np.pi} to relative_longitude {relative_longitude}')
            relative_longitude.value += np.pi

        if surface_orientation.radians > np.pi and relative_longitude.value > 0:
            print(f'[bold red]Remove[/bold red] {np.pi} from relative_longitude {relative_longitude}')
            relative_longitude.value -= np.pi
        print(f'Relative longitude Adjusted ? : {relative_longitude}')
        ```

        Manually testing the adjustment, seems to invert logical results in a
        way such as :

        - If the panel looks east (90 degrees orientation), then it shows
        zero-to-somewhat-low power output values in the morning than when looking west.

        - If the panel looks west (270 degrees), the opposite output is
        generated : high power output in the morning and 0-to-somewhat-low
        output in the evening.

      3. negative solar hour angle for the incidence angle

    """
    solar_altitude_series = calculate_solar_altitude_time_series_jenco(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )
    solar_azimuth_series = calculate_solar_azimuth_time_series_jenco(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )  # Origin ?
    in_shade = is_surface_in_shade_time_series(
        solar_altitude_series=solar_altitude_series,
        solar_azimuth_series=solar_azimuth_series,
        shadow_indicator=shadow_indicator,
        horizon_heights=horizon_heights,
        horizon_interval=horizon_interval,
        log=log,
    )
    if np.all(in_shade):
        return NO_SOLAR_INCIDENCE

    else:
        sine_relative_inclined_latitude = -(
            cos(latitude.radians)
            * sin(surface_tilt.radians)
            * cos(surface_orientation.radians)
            + sin(latitude.radians) * cos(surface_tilt.radians)
        )
        relative_inclined_latitude = asin(sine_relative_inclined_latitude)
        solar_declination_series = calculate_solar_declination_time_series_noaa(
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            log=log,
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
            dtype=dtype,
            array_backend=array_backend,
            log=log,
        )
        relative_longitude = calculate_relative_longitude(
            latitude=latitude,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            dtype=dtype,
            log=log,
        )
        # Note the - in front of the solar_hour_angle_series ! Explain-Me !
        sine_solar_incidence_series = (
            c_inclined_31_series * np.cos(-solar_hour_angle_series.radians - relative_longitude.radians)
            + c_inclined_33_series
        )
        solar_incidence_series = np.arcsin(sine_solar_incidence_series)

    incidence_angle_definition = SolarIncidence().definition_complementary
    incidence_angle_description = SolarIncidence().description_complementary
    if not complementary_incidence_angle:
        logger.info(':information: [bold][magenta]Converting[/magenta] solar incidence angle to {COMPLEMENTARY_INCIDENCE_ANGLE_DEFINITION}[/bold]...')
        solar_incidence_series = (pi / 2) - solar_incidence_series
        incidence_angle_definition = SolarIncidence().definition
        incidence_angle_description = SolarIncidence().description

    # set negative or below horizon angles to 0 !
    solar_incidence_series[
        (solar_incidence_series < 0) | (solar_altitude_series.value < 0)
    ] = NO_SOLAR_INCIDENCE

    log_data_fingerprint(
            data=solar_incidence_series,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return SolarIncidence(
        value=solar_incidence_series,
        unit=RADIANS,
        positioning_algorithm=solar_azimuth_series.position_algorithm,  #
        timing_algorithm=solar_hour_angle_series.timing_algorithm,  #
        incidence_algorithm=SolarIncidenceModel.jenco,
        definition=incidence_angle_definition,
        description=incidence_angle_description,
    )
