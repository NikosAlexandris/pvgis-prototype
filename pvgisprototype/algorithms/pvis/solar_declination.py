from devtools import debug
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pandas import DatetimeIndex
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarDeclinationPVISInputModel
from datetime import datetime
from pvgisprototype import SolarDeclination
from pvgisprototype.algorithms.pvis.fractional_year import calculate_day_angle_series_hofierka, calculate_fractional_year_pvis
from math import sin
from math import asin
from math import isfinite
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
import numpy
from pvgisprototype.api.position.models import SolarPositionModel


@validate_with_pydantic(CalculateSolarDeclinationPVISInputModel)
def calculate_solar_declination_pvis(
    timestamp: datetime,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
) -> SolarDeclination:
    """Approximate the sun's declination for a given day of the year.

    The solar declination is the angle between the Sun's rays and the
    equatorial plane of Earth. It varies throughout the year due to the tilt of
    the Earth's axis and is an important parameter in determining the seasons
    and the amount of solar radiation received at different latitudes.

    The function calculates the `proportion` of the way through the year (in
    radians), which is given by `(2 * pi * day_of_year) / 365.25`.
    The `0.3978`, `1.4`, and `0.0355` are constants in the approximation
    formula, with the `0.0489` being an adjustment factor for the slight
    eccentricity of Earth's orbit.
  
    Parameters
    ----------
    day_of_year: int
        The day of the year (ranging from 1 to 365 or 366 in a leap year).

    Returns
    -------
    solar_declination: float
        The solar declination in radians for the given day of the year.

    Notes
    -----

    The equation used here is a simple approximation and bases upon a direct
    translation from PVGIS' rsun3 source code:

      - from file: rsun_base.cpp
      - function: com_declin(no_of_day)

    For more accurate calculations of solar position, comprehensive models like
    the Solar Position Algorithm (SPA) are typically used.
    """
    fractional_year = calculate_fractional_year_pvis(
        timestamp=timestamp,
    )
    # Note the - sign for the output solar declination, as is in PVGIS v5.2
    # see : com_declin() in rsun_base.c
    solar_declination = - asin(
        0.3978
        * sin(
            fractional_year.radians
            - 1.4
            + eccentricity_correction_factor
            * sin(fractional_year.radians - perigee_offset)
        )
    )
    solar_declination = SolarDeclination(
        value=solar_declination,
        unit=RADIANS,
        position_algorithm='PVIS',
        timing_algorithm='PVIS',
    )
    if (
        not isfinite(solar_declination.degrees)
        or not solar_declination.min_degrees <= solar_declination.degrees <= solar_declination.max_degrees
    ):
        raise ValueError(
            f"The calculated solar declination angle {solar_declination.degrees} is out of the expected range\
            [{solar_declination.min_degrees}, {solar_declination.max_degrees}] degrees"
        )
    return solar_declination


# @validate_with_pydantic(CalculateSolarDeclinationPVISInputModel)
@log_function_call
@cached(cache={}, key=custom_hashkey)
def calculate_solar_declination_series_hofierka(
    timestamps: DatetimeIndex,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarDeclination:
    """Approximate the sun's declination for a given day of the year.

    The solar declination is the angle between the Sun's rays and the
    equatorial plane of Earth. It varies throughout the year due to the tilt of
    the Earth's axis and is an important parameter in determining the seasons
    and the amount of solar radiation received at different latitudes.

    The function calculates the `proportion` of the way through the year (in
    radians), which is given by `(2 * pi * day_of_year) / 365.25`.
    The `0.3978`, `1.4`, and `0.0355` are constants in the approximation
    formula, with the `0.0489` being an adjustment factor for the slight
    eccentricity of Earth's orbit.
  
    Parameters
    ----------
    day_of_year: int
        The day of the year (ranging from 1 to 365 or 366 in a leap year).

    Returns
    -------
    solar_declination: float
        The solar declination in radians for the given day of the year.

    Notes
    -----

    The equation used here is a simple approximation and bases upon a direct
    translation from PVGIS' rsun3 source code:

      - from file: rsun_base.cpp
      - function: com_declin(no_of_day)

    For more accurate calculations of solar position, comprehensive models like
    the Solar Position Algorithm (SPA) are typically used.
    """
    day_angle_series = calculate_day_angle_series_hofierka(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    # Note the - sign for the output solar declination, as is in PVGIS v5.2
    # see : com_declin() in rsun_base.c
    solar_declination_series = numpy.arcsin(
        0.3978
        * numpy.sin(
            day_angle_series.radians
            - 1.4
            + eccentricity_correction_factor
            * numpy.sin(day_angle_series.radians - perigee_offset)
        )
    )
    if (
        (solar_declination_series < SolarDeclination().min_radians)
        | (solar_declination_series > SolarDeclination().max_radians)
    ).any():
        out_of_range_values = solar_declination_series[
            (solar_declination_series < SolarDeclination().min_radians)
            | (solar_declination_series > SolarDeclination().max_radians)
        ]
        # raise ValueError(# ?
        logger.warning(
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{SolarDeclination().min_radians}, {SolarDeclination().max_radians}] radians"
            f" in [code]solar_declination_series[/code] : {out_of_range_values}"
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_declination_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarDeclination(
        value=solar_declination_series,
        unit=RADIANS,
        position_algorithm=SolarPositionModel.hofierka,  # ?
    )
