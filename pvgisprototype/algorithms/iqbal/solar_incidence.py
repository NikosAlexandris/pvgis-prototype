"""
Calculate the solar incidence angle for a surface that is tilted to any
horizontal and vertical angle, as described by Iqbal [0].

[0] Iqbal, M. “An Introduction to Solar Radiation”. New York: 1983; pp. 23-25.
"""

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
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import COMPLEMENTARY_INCIDENCE_ANGLE_FALSE
from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_azimuth import calculate_solar_azimuth_time_series_noaa
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from pvgisprototype.constants import NO_SOLAR_INCIDENCE
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from math import pi


def calculate_solar_incidence_time_series_iqbal(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: Optional[ZoneInfo] = None,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_FALSE,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
)-> SolarIncidence:
    """Calculate the solar incidence angle between the sun position unit vector and the surface normal unit vector; in other words, the cosine of the angle of incidence.

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
    solar_hour_angle_series = calculate_solar_hour_angle_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_zenith_series = calculate_solar_zenith_time_series_noaa(
        latitude=latitude,
        timestamps=timestamps,
        solar_hour_angle_series=solar_hour_angle_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_azimuth_series = calculate_solar_azimuth_time_series_noaa(
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

    # named 'projection' in pvlib
    cosine_solar_incidence_series = (
        cos(surface_tilt.radians)
        * numpy.cos(solar_zenith_series.radians)
        + sin(surface_tilt.radians) 
        * numpy.sin(solar_zenith_series.radians)
        * numpy.cos(solar_azimuth_series.radians - surface_orientation.radians)
    )

    # GH 1185 : This is a note from pvlib ?
    # projection = numpy.clip(projection, -1, 1)
    cosine_solar_incidence_series = numpy.clip(cosine_solar_incidence_series, -1, 1)
    solar_incidence_series = numpy.arccos(cosine_solar_incidence_series)

    description='Incidence angle between sun-vector and surface-normal'
    incidence_definition='Sun-to-Surface-Normal'
    if complementary_incidence_angle:  # derive the 'typical' incidence angle
        solar_incidence_series = (pi / 2) - solar_incidence_series
        description = "The 'complementary' incidence angle between the position of the sun (sun-vector) and the inclination angle of a surface (surface-plane)."
        incidence_definition='Sun-to-Plane'

    # set negative or below horizon angles ( == solar zenith > 90 ) to 0 !
    solar_incidence_series[
        (solar_incidence_series < 0) | (solar_zenith_series.value > pi / 2)
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
        incidence_algorithm=SolarIncidenceModel.iqbal,
        definition=incidence_definition,
        description=description,
    )
