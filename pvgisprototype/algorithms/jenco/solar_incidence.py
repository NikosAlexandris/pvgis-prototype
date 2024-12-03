from math import asin, cos, pi, sin
from pathlib import Path
from typing import List
from zoneinfo import ZoneInfo

import numpy as np
from devtools import debug
from pandas import DatetimeIndex
from pydantic_numpy import NpNDArray
from xarray import DataArray

from pvgisprototype import (
    Latitude,
    Longitude,
    RelativeLongitude,
    SolarIncidence,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.algorithms.jenco.solar_altitude import (
    calculate_solar_altitude_series_jenco,
)
from pvgisprototype.algorithms.jenco.solar_azimuth import (
    calculate_solar_azimuth_series_jenco,
)
from pvgisprototype.algorithms.jenco.solar_declination import (
    calculate_solar_declination_series_jenco,
)
from pvgisprototype.algorithms.noaa.solar_hour_angle import (
    calculate_solar_hour_angle_series_noaa,
)
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    COMPLEMENTARY_INCIDENCE_ANGLE_DEFINITION,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    NO_SOLAR_INCIDENCE,
    PERIGEE_OFFSET,
    RADIANS,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.validation.functions import (
    CalculateRelativeLongitudeInputModel,
    CalculateSolarIncidenceTimeSeriesJencoInputModel,
    validate_with_pydantic,
)


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
    Hofierka (2002) uses equations presented by Jenčo (1992) :

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
        sin(surface_tilt.radians) * sin(surface_orientation.radians)
    )
    tangent_relative_longitude_denominator = -(
        sin(latitude.radians)
        * sin(surface_tilt.radians)
        * cos(surface_orientation.radians)
        + cos(latitude.radians) * cos(surface_tilt.radians)
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


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateSolarIncidenceTimeSeriesJencoInputModel)
def calculate_solar_incidence_series_jenco(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo | None,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    surface_in_shade_series: NpNDArray | None = None,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarIncidence:
    """Calculate the solar incidence angle between the position of the sun and
    a reference solar surface.

    Calculate the solar incidence angle based on the position of the sun
    (sun-vector) and the a reference solar surface. Typically the solar
    incidence is the angle between the sun-vector and the normal to the solar
    surface (surface-normal). However, the underlying functions that convert
    horizontal irradiance components to inclined, expect the complementary
    incidence angle which is defined as the angle between the sun-vector and
    the inclination or plane of the reference solar surface (surface-plane).
    We call this the "complementary" incidence angle contrasting typical
    definitions of the incidence angle between the sun-vector and the normal to
    the surface in question. Alternatively the function can return the angle
    between the sun-vector and the normal vector to the reference surface.

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
    The solar incidence angle is the single most important quantity in the
    solar geometry setup. Its definition will affect all subsequent operations
    excluding none of the irradiance components, nor the photovoltaic power or
    energy estimations.

    Attention! There is no one, and only one, definition of the solar incidence
    angle! While many authors refer to the angle between the sun-vector and the
    normal to the reference surface, for example Martin and Ruiz (2002, 2005),
    others, like for example Jenčo (1992) and Hofierka (2002), consider as
    incidence the angle between the sun-vector and the reference surface-plane.
    These angles are complementary to each other. This fact is an important one
    when treating trigonometric relationships that affect the calculation of
    the incidence angle.

    In this program, we implement and consider as _complementary_ the incidence
    angle as defined by Jenčo (1992) between the direction of the sun-rays and
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

    Reading the paper by Jenčo (1992) [1]_ (last page is a summary translation in
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
    by Jenčo (1992) who measures the incidence angle between the sun-vector and
    plane of the reference solar surface. Care needs to be taken when comparing
    or using other definitions of the solar incidence angle.

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

    - Shadow check not implemented.
    """
    # Identify times without solar insolation
    solar_altitude_series = calculate_solar_altitude_series_jenco(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )
    solar_azimuth_east_based_series = calculate_solar_azimuth_series_jenco(
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

    # from pvgisprototype import SolarAzimuth
    # solar_azimuth_series = SolarAzimuth(
    #     value=(solar_azimuth_east_based_series.value + np.pi/2),
    #     unit=RADIANS,
    # )

    # Prepare relevant quantities
    sine_relative_inclined_latitude = -cos(latitude.radians) * sin(
        surface_tilt.radians
    ) * cos(surface_orientation.radians) + sin(latitude.radians) * cos(
        surface_tilt.radians
    )
    relative_inclined_latitude = asin(sine_relative_inclined_latitude)

    solar_declination_series = calculate_solar_declination_series_jenco(
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
    solar_hour_angle_series = calculate_solar_hour_angle_series_noaa(
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
        c_inclined_31_series
        * np.cos(solar_hour_angle_series.radians - relative_longitude.radians)
        + c_inclined_33_series
    )
    solar_incidence_series = np.arcsin(sine_solar_incidence_series)

    incidence_angle_definition = SolarIncidence().definition_complementary
    incidence_angle_description = SolarIncidence().description_complementary
    if not complementary_incidence_angle:
        logger.info(
            f":information: Converting solar incidence angle to {COMPLEMENTARY_INCIDENCE_ANGLE_DEFINITION}...",
            alt=f":information: [bold][magenta]Converting[/magenta] solar incidence angle to {COMPLEMENTARY_INCIDENCE_ANGLE_DEFINITION}[/bold]..."
        )
        solar_incidence_series = (pi / 2) - solar_incidence_series
        incidence_angle_definition = SolarIncidence().definition
        incidence_angle_description = SolarIncidence().description

    # Combined mask for no solar incidence, negative solar incidence or below horizon angles
    mask_below_horizon_or_in_shade = (
        solar_altitude_series.radians < 0
    ) | surface_in_shade_series.value

    mask_no_solar_incidence_series = (
        solar_incidence_series < 0
    ) | mask_below_horizon_or_in_shade

    if zero_negative_solar_incidence_angle:
        solar_incidence_series = np.where(
            mask_no_solar_incidence_series,
            # (solar_incidence_series < 0) | (solar_altitude_series.value < 0),
            NO_SOLAR_INCIDENCE,
            solar_incidence_series,
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_incidence_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarIncidence(
        value=solar_incidence_series,
        unit=RADIANS,
        positioning_algorithm=solar_declination_series.position_algorithm,  #
        timing_algorithm=solar_hour_angle_series.timing_algorithm,  #
        incidence_algorithm=SolarIncidenceModel.jenco,
        definition=incidence_angle_definition,
        description=incidence_angle_description,
        # azimuth_origin=solar_azimuth_east_based_series.origin,
    )
