from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarDeclinationPVISInputModel
from datetime import datetime
from pvgisprototype import SolarDeclination
from pvgisprototype.algorithms.pvis.fractional_year import calculate_fractional_year_pvis
from math import sin
from math import asin
from math import isfinite
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RADIANS


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
    solar_declination = asin(
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
