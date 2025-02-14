from pandas import Timestamp
from pvgisprototype.constants import TIMEZONE_UTC
from functools import partial
from math import isfinite, radians, sin

from pvgisprototype import SolarDeclination
from pvgisprototype.api.utilities.timestamp import get_days_in_year
from pvgisprototype.constants import DEGREES
from pvgisprototype.validation.functions import (
    CalculateSolarDeclinationHargreavesInputModel,
    validate_with_pydantic,
)


@validate_with_pydantic(CalculateSolarDeclinationHargreavesInputModel)
def calculate_solar_declination_hargreaves(
    timestamp: Timestamp = partial(Timestamp.now(tz=TIMEZONE_UTC)),
) -> SolarDeclination:
    """Approximate the solar declination based on the Hargreaves formula.

                     ⎛360   ⎛                    ⎛360            ⎞⎞⎞
    δ = 23.45° ⋅ sin ⎜─── ⋅ ⎜284 + n + 0.4 ⋅ sin ⎜─── ⋅ (n - 100)⎟⎟⎟
                     ⎝365   ⎝                    ⎝365            ⎠⎠⎠

    Notes
    -----

    - 365.25: The number 365.25 represents the average number of days in a
    year. This value is used to scale the orbital position of the Earth.

    - 284: The number 284 represents a constant term added to the day of the
    year. It adjusts the calculation to align with the Earth's position
    during the winter solstice, which usually occurs around December 21st
    (approximately 284 days into the year).

    - 0.4: The number 0.4 is a constant that determines the amplitude of the
    seasonal variation. It is multiplied by the second sine term to
    modulate the seasonal change in the solar declination.

    - 100: The number 100 represents an offset to the day of the year. It is
    subtracted from the original day of the year before calculating the
    second sine term. This offset helps adjust the timing of the seasonal
    variation and is usually chosen to align with the summer solstice,
    which typically occurs around June 21st.
    """
    days_in_year = get_days_in_year(timestamp.year)
    day_of_year = timestamp.timetuple().tm_yday
    declination_value_in_degrees = 23.45 * sin(
        radians(
            360
            / days_in_year
            * (
                284
                + day_of_year
                + 0.4 * sin(radians(360 / days_in_year * (day_of_year - 100)))
            )
        )
    )
    solar_declination = SolarDeclination(
        value=declination_value_in_degrees,
        unit=DEGREES,
        position_algorithm="Hargreaves",
        timing_algorithm="Hargreaves",
    )
    if (
        not isfinite(solar_declination.degrees)
        or not solar_declination.min_degrees
        <= solar_declination.degrees
        <= solar_declination.max_degrees
    ):
        raise ValueError(
            f"The calculated solar declination angle {solar_declination.degrees} is out of the expected range\
            [{solar_declination.min_degrees}, {solar_declination.max_degrees}] degrees"
        )
    return solar_declination
