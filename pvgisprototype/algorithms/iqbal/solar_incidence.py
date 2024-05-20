"""
Calculate the solar incidence angle for a surface that is tilted to any
horizontal and vertical angle, as described by Iqbal [0].

[0] Iqbal, M. “An Introduction to Solar Radiation”. New York: 1983; pp. 23-25.
"""

from pvgisprototype.log import log_function_call
from math import cos, sin
import numpy
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pandas import DatetimeIndex 
from typing import Optional
from zoneinfo import ZoneInfo
from pvgisprototype import SurfaceOrientation
from pvgisprototype import SurfaceTilt
from pvgisprototype import SolarZenith
from pvgisprototype import SolarAzimuth
from pvgisprototype import SolarIncidence
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.constants import LOSS_NAME, SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_azimuth import calculate_solar_azimuth_time_series_noaa
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from pvgisprototype.constants import NO_SOLAR_INCIDENCE
from pvgisprototype.constants import RADIANS
from math import pi
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.validation.arrays import create_array


@log_function_call
def calculate_solar_incidence_time_series_iqbal(
    longitude: Longitude,
    latitude: Latitude,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex = now_utc_datetimezone(),
    timezone: ZoneInfo | None = None,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
)-> SolarIncidence:
    """Calculate the solar incidence angle for a surface oriented in any
    direction.

    Calculate the solar incidence angle between the sun position unit vector
    and the surface normal unit vector for a surface oriented in any direction;
    in other words, the cosine of the angle of incidence. Optionally, the
    output may be the complementary incidence angle between the direction of
    the sun-to-surface vector and the direction of the surface plane.

    Notes
    -----

    The equation for the incidence angle `I` by Iqbal (1983) [0]_ [1]_

        I = Arc cos( cos(θ) * cos(ω) + sin(ω) * sin(θ) * (Γ - γ) )

    where :

    - θ is the solar zenith angle
    - ω is the surface tilt angle
    - Γ is the astronomers topocentric azimuth angle
    - γ is the navigators topocentric azimuth angle

    Important observations are :

    - The topocentric astronomers azimuth angle `Γ` which is measured _westward
      from south_.

    - The surface orientation angle `γ` (also referred to as surface azimuth
      rotation angle) is measured from south to the projection of the surface
      normal on the horizontal plane, positive or negative if oriented west or
      east from south, respectively.

    - The topocentric azimuth angle `Φ` for navigators and solar radiation
      users (equation 46, p. 588) is measured _eastward from north_ and thus
      equals the astronomers one plus π or else 180 degrees :

       Φ = Γ + 180

       and thus

       Γ = Φ - 180    [*]

    In equation I, the surface orientation angle `γ` measured from south, is
    subtracted from the astronomers topocentric azimuth angle which is likewise
    measured from south. Given that most applications measure azimuthal angles
    from North, care must be taken to feed the correct "version" of these
    angles in this function.

    PVGIS measures the user-requested azimuthal angles solar azimuth, follownig
    denoted also with Φ, and the "solar radiation"-relevant surface orientation
    from North, follownig denoted as `γΝ`. Equation I based on [*] becomes
    relevant for PVGIS in the follownig form :

        I = Arc cos( cos(θ) * cos(ω) + sin(ω) * sin(θ) * (Φ - 180 - γN - 180) )

        or else

        cosine_solar_incidence_series = (
            numpy.cos(solar_zenith_series.radians)
            * cos(surface_tilt.radians)
            + sin(surface_tilt.radians) 
            * numpy.sin(solar_zenith_series.radians)
            * numpy.cos(solar_azimuth_series.radians -
            surface_orientation.radians - 2 * pi)
        )

    Nonetheless, and for the sake of consistency with the author's original
    definition, such conversion are preferrable to be performed in advance and
    outside the scope of the current function, for both the solar azimuth and
    the surface orientation angles. Therefore the internal form of the equation
    uses as per its definition the astronomers topocentric solar azimuth angle
    and the surface azimuth rotation angle measured from south -- see also
    source code of this function.

    References
    ----------
    .. [0] Iqbal, 1983

    .. [1] Equation 47, p. 588),
 
    Parameters
    ----------
    longitude : Longitude
    latitude : Latitude
    timestamps : DatetimeIndex
    timezone : ZoneInfo
    surface_orientation : SurfaceOrientation
        Panel azimuth from north.
    surface_tilt : SurfaceTilt
        Panel tilt from horizontal.
    apply_atmospheric_refraction : bool
    complementary_incidence_angle : bool
    dtype : str
    array_backend : str
    verbose : int
    log : int

    Returns
    -------
    solar_incidence_series : SolarIncidence
        A times series of solar incidence angles between the sun position
        vector and the surface normal (or plane)

    Notes
    -----
    Notes from the original pvlib function :

    - Usage note: When the sun is behind the surface the value returned is
      negative.  For many uses negative values must be set to zero.

    - Input all angles in degrees.

    References
    ----------
    .. [0] Iqbal, M. “An Introduction to Solar Radiation”. New York: 1983; pp. 23-25.

    """
    solar_zenith_series = calculate_solar_zenith_time_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_azimuth_series_north_based = calculate_solar_azimuth_time_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )  # North = 0 according to NOAA's solar geometry equations

    # array_parameters = {
    #     "shape": timestamps.shape,
    #     "dtype": dtype,
    #     "init_method": "empty",
    #     "backend": array_backend,
    # }  # Borrow shape from timestamps
    # solar_incidence_series = create_array(**array_parameters)

    # Convert to south-based
    solar_azimuth_series = SolarAzimuth(
        value=((solar_azimuth_series_north_based.radians - pi)),
        unit=RADIANS,
    )
    # Φimit Φ to the range from 0° to 360°.
    # Divide Φ by 360, record the decimal fraction of the division as F.
    # Divide phi by 360 and get the remainder and the fractional part
    fraction_series, _ = numpy.modf(solar_azimuth_series.radians / (2 * pi))

    # If Φ is positive, then the limited Φ = 360 * F .
    # If Φ is negative, then the limited Φ = 360 - 360 *F.

    solar_azimuth_series = SolarAzimuth(
        value=numpy.where(
            solar_azimuth_series.radians >= 0,
            2 * pi * fraction_series,
            2 * pi - (2 * pi * numpy.abs(fraction_series)),
        ),
        unit=RADIANS,
    )
    # named 'projection' in pvlib
    cosine_solar_incidence_series = (
        numpy.cos(solar_zenith_series.radians)
        * cos(surface_tilt.radians)
        + sin(surface_tilt.radians) 
        * numpy.sin(solar_zenith_series.radians)
        * numpy.cos(solar_azimuth_series.radians - surface_orientation.radians)
        ) # where : 
    # solar_azimuth_series : is the astronomers topocentric solar azimuth measured from south
    # surface_orientation : is the surface rotation azimuth angle measured from south

    # GH 1185 : This is a note from pvlib ?
    # projection = numpy.clip(projection, -1, 1)
    cosine_solar_incidence_series = numpy.clip(cosine_solar_incidence_series, -1, 1)
    solar_incidence_series = numpy.arccos(cosine_solar_incidence_series)

    incidence_angle_definition = SolarIncidence().definition
    incidence_angle_description = SolarIncidence().description
    if complementary_incidence_angle:
        logger.info(':information: [bold][magenta]Converting[/magenta] solar incidence angle to {COMPLEMENTARY_INCIDENCE_ANGLE_DEFINITION}[/bold]...')
        solar_incidence_series = (pi / 2) - solar_incidence_series
        incidence_angle_definition = SolarIncidence().definition_complementary
        incidence_angle_description = SolarIncidence().description_complementary

    # set negative or below horizon angles ( == solar zenith > 90 ) to 0 !
    # mask_below_horizon = solar_zenith_series.value > pi/2
    # solar_incidence_series[mask_below_horizon] = 0
    solar_incidence_series[
        (solar_incidence_series < 0) | (solar_zenith_series.radians > pi / 2)
    ] = NO_SOLAR_INCIDENCE

    # solar_incidence_series = numpy.where(
    #     (solar_incidence_series < 0) | (solar_zenith_series.radians > pi / 2),
    #     NO_SOLAR_INCIDENCE,
    #     solar_incidence_series,
    # )

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
        positioning_algorithm=solar_zenith_series.position_algorithm,  #
        timing_algorithm=solar_zenith_series.timing_algorithm,  #
        incidence_algorithm=SolarIncidenceModel.iqbal,
        definition=incidence_angle_definition,
        description=incidence_angle_description,
    )
