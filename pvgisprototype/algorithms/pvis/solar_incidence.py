from pvgisprototype.log import logger
from pandas import DatetimeIndex
from devtools import debug
from numpy import number
import numpy
from pvgisprototype.algorithms.pvis.solar_altitude import calculate_solar_altitude_series_hofierka
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarIncidencePVISInputModel
from pvgisprototype import SolarIncidence
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import RelativeLongitude
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.constants import PERIGEE_OFFSET, ZERO_NEGATIVE_SOLAR_INCIDENCE_ANGLES_DEFAULT
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RADIANS
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_series_hofierka
from pvgisprototype.algorithms.pvis.solar_hour_angle import calculate_solar_hour_angle_series_hofierka
from math import pi, sin, asin, cos, acos
from pvgisprototype import SurfaceTilt
from pvgisprototype import SurfaceOrientation
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import RANDOM_DAY_SERIES_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from pvgisprototype.constants import NO_SOLAR_INCIDENCE
from pvgisprototype import SolarIncidence
from pvgisprototype.api.position.models import SolarIncidenceModel


@log_function_call
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
    tangent_relative_longitude_numerator = (
        - sin(surface_tilt.radians)             # cos(pi/2 - surface_tilt.radians)
        * -sin(surface_orientation.radians)     # cos(pi/2 + surface_orientation.radians)
    )
    tangent_relative_longitude_denominator = (
        sin(latitude.radians)
        * sin(surface_tilt.radians)             # cos(pi/2 - surface_tilt.radians)
        * cos(surface_orientation.radians)      # sin(pi/2 + surface_orientation.radians)
        + cos(latitude.radians)
        * cos(surface_tilt.radians)             # sin(pi/2 - surface_tilt.radians)
    )
    # force dtype !
    relative_longitude = numpy.array(
        [numpy.arctan(tangent_relative_longitude_numerator / tangent_relative_longitude_denominator)],
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


from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
# @validate_with_pydantic(CalculateSolarIncidencePVISInputModel)
def calculate_solar_incidence_pvis(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    surface_tilt: float = 0,
    surface_orientation: float = 180,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    log: int = 0,
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
    solar_incidence = acos(
        sin(latitude.radians)
        * (
            sin(solar_declination.radians)
            * cos(surface_tilt.radians)
            + cos(solar_declination.radians)
            * cos(surface_orientation.radians)
            * cos(hour_angle.radians)
            * sin(surface_tilt.radians)
        )
        + cos(latitude.radians)
        * (
            cos(solar_declination.radians)
            * cos(hour_angle.radians)
            * cos(surface_tilt.radians)
            - sin(solar_declination.radians)
            * cos(surface_orientation.radians)
            * sin(surface_tilt.radians)
        )
        + cos(solar_declination.radians)
        * sin(surface_orientation.radians)
        * sin(hour_angle.radians)
        * sin(surface_tilt.radians)
    )

    return SolarIncidence(value=solar_incidence, unit=RADIANS)


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
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_SOLAR_INCIDENCE_ANGLES_DEFAULT,
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

    # Idea for alternative solar time modelling, i.e. Milne 1921 -------------
    # solar_time = model_solar_time(
    #     longitude=longitude,
    #     latitude=latitude,
    #     timestamp=timestamp,
    #     timezone=timezone,
    #     solar_time_model=solar_time_model,  # returns datetime.time object
    #     perigee_offset=perigee_offset,
    #     eccentricity_correction_factor=eccentricity_correction_factor,
    # )
    # hour_angle = calculate_solar_hour_angle_pvis(
    #         solar_time=solar_time,
    # )
    # ------------------------------------------------------------------------
    
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

    # solar_incidence_series = numpy.arccos(
    #     sin(latitude.radians)
    #     * (
    #         numpy.sin(solar_declination_series.radians)
    #         * cos(surface_tilt.radians)
    #         + numpy.cos(solar_declination_series.radians)
    #         * cos(surface_orientation.radians)
    #         * numpy.cos(solar_hour_angle_series.radians)
    #         * sin(surface_tilt.radians)
    #     )
    #     + cos(latitude.radians)
    #     * (
    #         numpy.cos(solar_declination_series.radians)
    #         * numpy.cos(solar_hour_angle_series.radians)
    #         * cos(surface_tilt.radians)
    #         - numpy.sin(solar_declination.radians)
    #         * cos(surface_orientation.radians)
    #         * sin(surface_tilt.radians)
    #     )
    #     + numpy.cos(solar_declination_series.radians)
    #     * sin(surface_orientation.radians)
    #     * numpy.sin(solar_hour_angle_series.radians)
    #     * sin(surface_tilt.radians)
    # )

    # Prepare relevant quantities as in PVGIS v5.2
    sine_relative_inclined_latitude = (
        - cos(latitude.radians)
        * sin(surface_tilt.radians)             # cos(pi/2 - surface_tilt.radians)
        * cos(surface_orientation.radians)      # sin(pi/2 + surface_orientation.radians)
        + sin(latitude.radians)
        * cos(surface_tilt.radians)             # sin(pi/2 - surface_tilt.radians)
    )
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
        c_inclined_31_series * numpy.cos(-solar_hour_angle_series.radians - relative_longitude.radians)
        # c_inclined_31_series * numpy.cos(solar_hour_angle_series.radians - relative_longitude.radians)
        + c_inclined_33_series
    )
    solar_incidence_series = numpy.arcsin(sine_solar_incidence_series)
    
    incidence_angle_definition = SolarIncidence().definition_complementary
    incidence_angle_description = SolarIncidence().description_complementary
    if not complementary_incidence_angle:
        logger.info(':information: [bold][magenta]Converting[/magenta] solar incidence angle to {COMPLEMENTARY_INCIDENCE_ANGLE_DEFINITION}[/bold]...')
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
