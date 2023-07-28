import typer
from typing import Annotated
from typing import Optional
from typing import NamedTuple
from datetime import datetime
from datetime import timedelta
from ...api.utilities.conversions import convert_to_radians
from ...api.utilities.timestamp import now_utc_datetimezone
from ...api.utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.api.named_tuples import generate
from pvgisprototype.api.input_models import Longitude
from pvgisprototype.api.input_models import Latitude
from pvgisprototype.api.input_models import SolarTimeInput
from pvgisprototype.api.decorators import validate_with_pydantic
from math import radians
from math import sin
from math import cos
import numpy as np


@validate_with_pydantic(SolarTimeInput, expand_args=True)
def calculate_solar_time_eot(
        longitude: Longitude,
        latitude: Latitude,
        timestamp: datetime,
        timezone: str = None,
        days_in_a_year: float = 365.25,
        perigee_offset: float = 0.048869,
        orbital_eccentricity: float = 0.03344,
        time_offset_global: float = 0,
        hour_offset: float = 0,
)-> NamedTuple:
    """Calculate the solar time.

    - Local Time (LT)

    - Local Standard Time Meridian (LSTM)
    
        - 15° = 360°/24 hours.
        - Examples:
            - Sydney Australia is UTC +10 so the LSTM is 150 °E.
            - Phoenix, USA is UTC -7 so the LSTM is 105 °W

    - The equation of time (EoT) (in minutes) is an empirical equation that
      corrects for the eccentricity of the Earth's orbit and the Earth's axial
      tilt. An approximation accurate to within ½ minute is:

      EoT = 9.87 * sin(2*B) - 7.53 * cos(B) - 1.5 * sin(B)

        where:

        - DeltaTUTC : Local time minus UTC, in hours, also equal to the time zone
        - B = 360 / 365 * (day_of_year - 81)  # in degrees
        - Time correction (TC) factor = 4 * (longitude - LSTM) + EoT

    - Solar time (or local solar time) = LT + TC / 60
    - Hour angle = 15 * (LST - 12)

    Notes
    -----
    _Milne

    @article{Milne1921,
        doi = {10.2307/3604631},
        year = 1921,
        publisher = {Cambridge University Press ({CUP})},
        volume = {10},
        number = {155},
        pages = {372--375},
        author = {R. M. Milne},
        title = {593. Note on the Equation of Time},
        journal = {The Mathematical Gazette}
    }
    """
    # # Handle Me during input validation? -------------------------------------
    # if timezone != timestamp.tzinfo:
    #     try:
    #         timestamp = timestamp.astimezone(timezone)
    #     except Exception as e:
    #         logging.warning(f'Error setting tzinfo for timestamp = {timestamp}: {e}')
    # # Handle Me during input validation? -------------------------------------

    year = timestamp.year
    start_of_year = datetime(year=year, month=1, day=1, tzinfo=timestamp.tzinfo)
    hour_of_year = int((timestamp - start_of_year).total_seconds() / 3600)
    day_of_year = timestamp.timetuple().tm_yday

    # Equation of Time, Milne 1921 -------------------------------------------
    # The difference of local time from UTC equals the time zone, in hours
    local_time_minus_utc = timestamp.utcoffset().total_seconds() / 3600
    local_standard_meridian_time = 15 * local_time_minus_utc

    b = radians( 360 / 365 * (day_of_year - 81))  # from degrees to radians
    equation_of_time = 9.87 * sin(2*b) - 7.53 * cos(b) - 1.5 * sin(b)

    # ------------------------------------------------------------------------
    longitude = np.degrees(longitude)  # this equation of time requires degrees!
    # ------------------------------------------------------------------------

    time_correction_factor = 4 * (longitude - local_standard_meridian_time) + equation_of_time
    time_correction_factor_hours = time_correction_factor / 60
    solar_time = timestamp + timedelta(hours=time_correction_factor_hours)
    solar_time_decimal_hours = solar_time.hour + solar_time.minute / 60 + solar_time.second / 3600
    hour_angle = 15 * (solar_time_decimal_hours - 12)
    # ------------------------------------------------------------------------
    
    solar_time = generate('solar_time', (solar_time, 'decimal hours'))
    return solar_time
