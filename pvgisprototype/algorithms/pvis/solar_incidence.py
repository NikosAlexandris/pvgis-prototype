from math import asin, cos, pi, sin
from zoneinfo import ZoneInfo

import numpy
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import (
    Latitude,
    Longitude,
    RelativeLongitude,
    SolarIncidence,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.algorithms.pvis.solar_altitude import (
    calculate_solar_altitude_series_hofierka,
)
from pvgisprototype.algorithms.pvis.solar_declination import (
    calculate_solar_declination_series_hofierka,
)
from pvgisprototype.algorithms.pvis.solar_hour_angle import (
    calculate_solar_hour_angle_series_hofierka,
)
from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.position.models import SolarIncidenceModel, SolarTimeModel
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


@log_function_call
@custom_cached
# @validate_with_pydantic(CalculateRelativeLongitudeInputModel)
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
    tangent_relative_longitude_numerator = -sin(
        surface_tilt.radians
    ) * -sin(  # cos(pi/2 - surface_tilt.radians)
        surface_orientation.radians
    )  # cos(pi/2 + surface_orientation.radians)
    tangent_relative_longitude_denominator = sin(latitude.radians) * sin(
        surface_tilt.radians
    ) * cos(  # cos(pi/2 - surface_tilt.radians)
        surface_orientation.radians
    ) + cos(  # sin(pi/2 + surface_orientation.radians)
        latitude.radians
    ) * cos(
        surface_tilt.radians
    )  # sin(pi/2 - surface_tilt.radians)
    # force dtype !
    relative_longitude = numpy.array(
        [
            numpy.arctan(
                tangent_relative_longitude_numerator
                / tangent_relative_longitude_denominator
            )
        ],
        dtype=dtype,
    )

    if surface_orientation.radians < pi and relative_longitude < 0:
        relative_longitude += pi

    if surface_orientation.radians > pi and relative_longitude > 0:
        relative_longitude -= pi

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
# @validate_with_pydantic(CalculateSolarIncidenceTimeSeriesPVISInputModel)
def calculate_solar_incidence_series_hofierka(
    longitude: Longitude,
    latitude: Latitude,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex = str(now_utc_datetimezone()),
    timezone: ZoneInfo | None = None,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarIncidence:
    """Calculate the angle of incidence (θ) between the direction of the sun
    ray and the line normal to the surface measured in radian.

    θ =
    acos(
         sin(Φ)
         * (
           sin(δ) * cos(β) + cos(δ) * cos(γ) * cos(ω) * sin(β)
           )
         + cos(Φ) * (cos(δ) * cos(ω) * cos(β) - sin(δ) * cos(γ) * sin(β))
         + cos(δ)
         * sin(γ)
         * sin(ω)
         * sin(β)
        )

    Parameters
    ----------

    latitude: float
        Latitude is the angle (Φ) between the sun's rays and its projection on
        the horizontal surface measured in radian.

    surface_tilt: float
        Surface tilt or slope is the angle (β) between the inclined slope and
        the horizontal plane measured in radian.

    surface_orientiation: float
        Surface orientation or azimuth is the angle (γ) in the horizontal plane
        between the line due south and the horizontal projection of the normal
        to the inclined plane surface measured in radian.

    Returns
    -------
    solar_incidence: float
        The angle of incidence (θ) is the angle between the direction of the
        sun ray and the line normal to the surface measured in radian.
    """
    solar_declination_series = calculate_solar_declination_series_hofierka(
        timestamps=timestamps,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
    )
    solar_hour_angle_series = calculate_solar_hour_angle_series_hofierka(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
    )
    solar_altitude_series = calculate_solar_altitude_series_hofierka(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    sine_relative_inclined_latitude = -cos(latitude.radians) * sin(
        surface_tilt.radians
    ) * cos(  # cos(pi/2 - surface_tilt.radians)
        surface_orientation.radians
    ) + sin(  # sin(pi/2 + surface_orientation.radians)
        latitude.radians
    ) * cos(
        surface_tilt.radians
    )  # sin(pi/2 - surface_tilt.radians)
    relative_inclined_latitude = asin(sine_relative_inclined_latitude)
    c_inclined_31_series = cos(relative_inclined_latitude) * numpy.cos(
        solar_declination_series.radians
    )
    c_inclined_33_series = sin(relative_inclined_latitude) * numpy.sin(
        solar_declination_series.radians
    )
    relative_longitude = calculate_relative_longitude(
        latitude=latitude,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
    )
    sine_solar_incidence_series = (
        c_inclined_31_series
        * numpy.cos(-solar_hour_angle_series.radians - relative_longitude.radians)
        + c_inclined_33_series
    )
    solar_incidence_series = numpy.arcsin(sine_solar_incidence_series)

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

    # set negative or below horizon angles to 0 !
    if zero_negative_solar_incidence_angle:
        solar_incidence_series[
            (solar_incidence_series < 0) | (solar_altitude_series.value < 0)
        ] = NO_SOLAR_INCIDENCE

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
        incidence_algorithm=SolarIncidenceModel.hofierka,
        definition=incidence_angle_definition,
        description=incidence_angle_description,
        # azimuth_origin=solar_azimuth_series.origin,
    )
