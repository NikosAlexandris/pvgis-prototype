from devtools import debug
import typer
from typing import Annotated
from functools import partial
from datetime import datetime
from datetime import timezone
from math import sin
from math import cos
from math import radians
from pvgisprototype.api.utilities.conversions import convert_to_radians_if_requested
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarDeclinationHargreavesInputModel
from pvgisprototype import SolarDeclination


@validate_with_pydantic(CalculateSolarDeclinationHargreavesInputModel)
def calculate_solar_declination_hargreaves(
        timestamp: datetime = partial(datetime.now, tz=timezone.utc),
        days_in_a_year: float = 365.25,
        # angle_output_units: str = 'radians',
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
    # year = timestamp.year
    # start_of_year = datetime(year=year, month=1, day=1, tzinfo=timezone.utc)
    day_of_year = timestamp.timetuple().tm_yday
    declination_value_in_degrees = 23.45 * sin(
        radians(
            360
            / days_in_a_year
            * (
                284
                + day_of_year
                + 0.4
                * sin(radians(360 / days_in_a_year * (day_of_year - 100)))
            )
        )
    )
    # declination = generate('declination', )
    declination = SolarDeclination(value=declination_value_in_degrees, unit='degrees')
    # declination = convert_to_radians_if_requested(declination, angle_output_units)

    return declination
