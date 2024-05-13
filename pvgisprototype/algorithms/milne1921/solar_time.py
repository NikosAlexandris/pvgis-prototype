from devtools import debug
from numpy import True_
import typer
from rich import print
from typing import Annotated
from typing import Optional
from datetime import datetime
from datetime import timedelta

from math import radians
from math import degrees
from pvgisprototype.constants import MINUTES
from pvgisprototype import TrueSolarTime
from math import sin
from math import cos
from zoneinfo import ZoneInfo

from pvgisprototype import Longitude
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarTimeMilne1921InputModel


@validate_with_pydantic(CalculateSolarTimeMilne1921InputModel)
def calculate_apparent_solar_time_milne1921(
    longitude: Longitude,
    timestamp: datetime,
    verbose: int = 0,
) -> datetime:
    """Calculate the apparent solar time based on the equation of time by Milne 1921

    Notes
    -----

    - Local Time (LT)

    - Local Standard Time Meridian (LSTM)
    
        - 1 hour in time equals to 15° degrees of earth's rotation
          (from: 360°/24 hours)

        - Examples:
            - Sydney Australia is UTC +10 so the LSTM is 10 * 15° = 150 °E.
            - Phoenix, USA is UTC -7 so the LSTM is -7 * 15° = -105°E or 105 °W

    - The equation of time (EoT) (in minutes) is an empirical equation that
      corrects for the eccentricity of the Earth's orbit and the Earth's axial
      tilt. An approximation accurate to within ½ minute is:

      EoT = 9.87 * sin(2*B) - 7.53 * cos(B) - 1.5 * sin(B)

        where:

        - DeltaTUTC : Local time minus UTC, in hours, also equal to the time zone
        - B = 360 / 365 * (day_of_year - 81)  # in degrees
        - Time correction (TC) factor = 4 * (longitude - LSTM) + EoT

    - Solar time (or local solar time) = LT + TC / 60
        * The solar (or local) solar time here equals to :
        - the apparent solar time (AST)
        - or corrected local solar time
        - or true solar time or (TST)
        as termed in other models/equations.

    - Hour angle = 15 * (LST - 12)

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

    See also:

    @incollection{KALOGIROU201451,
    title = {Chapter 2 - Environmental Characteristics},
    editor = {Soteris A. Kalogirou},
    booktitle = {Solar Energy Engineering (Second Edition)},
    publisher = {Academic Press},
    edition = {Second Edition},
    address = {Boston},
    pages = {51-123},
    year = {2014},
    isbn = {978-0-12-397270-5},
    doi = {https://doi.org/10.1016/B978-0-12-397270-5.00002-9},
    url = {https://www.sciencedirect.com/science/article/pii/B9780123972705000029},
    author = {Soteris A. Kalogirou},
    keywords = {Atmospheric attenuation, Extraterrestrial radiation, Radiation exchange between surfaces, Shadow determination, Solar angles, Solar radiation measuring instruments, Solar radiation, Terrestrial irradiation, Total radiation on tilted surfaces, Typical meteorological year},
    abstract = {Chapter 2 gives an analysis of the environmental characteristics of solar radiation and in particular the reckoning of time and solar angles. In the latter the basic solar geometry equations are given including declination, hour angle, altitude angle, azimuth angle as well as the incidence angle for stationary and moving surfaces, sun path diagrams, and shadow determination including the way to calculate shading effects. This is followed by a description of the basic principles of solar radiation heat transfer including transparent plates, radiation exchange between surfaces, extraterrestrial solar radiation, atmospheric attenuation, terrestrial irradiation, and total radiation on tilted surfaces. It concludes with a review of the solar radiation measuring instruments and the way to construct typical meteorological year files.}
    }
    """
    # # Handle Me during input validation? -------------------------------------
    # if timezone != timestamp.tzinfo:
    #     try:
    #         timestamp = timestamp.astimezone(timezone)
    #     except Exception as e:
    #         logging.warning(f'Error setting tzinfo for timestamp = {timestamp}: {e}')
    # # Handle Me during input validation? -------------------------------------


    # Equation of Time, Milne 1921 -------------------------------------------

    # The difference of local time from UTC equals the time zone, in hours
    local_time_minus_utc = timestamp.utcoffset().total_seconds() / 3600
    local_standard_time_meridian = 15 * local_time_minus_utc

    # `b` for the equation of time -------------------------------------------
    day_of_year = timestamp.timetuple().tm_yday
    b = radians( 360 / 365 * (day_of_year - 81))  # from degrees to radians

    # however, in : 
    # Solar Energy Engineering (Second Edition),
    # Chapter 2 - Environmental Characteristics,
    # Soteris A. Kalogirou, Academic Press, 2014,
    # ISBN 9780123972705, https://doi.org/10.1016/B978-0-12-397270-5.00002-9.
    # Pages 51-123,
    # b = (day_of_year - 81) * 360 / 364  (in degrees)
    # -----------------------------------------------------------------------

    equation_of_time = 9.87 * sin(2 * b) - 7.53 * cos(b) - 1.5 * sin(b)

    # ------------------------------------------------------------------------
    # the following equation requires longitude in degrees!
    time_correction_factor = (
        4 * (longitude.degrees - local_standard_time_meridian) + equation_of_time
    )
    # ------------------------------------------------------------------------

    time_correction_factor_hours = time_correction_factor / 60
    apparent_solar_time = timestamp + timedelta(hours=time_correction_factor_hours)

    if verbose > 0:
        print('Day of year : {day_of_year}')
        print('Equation of time : {equation_of_time}')
        print('Time correction factor : {time_correction_factor}')

    if verbose == 3:
        debug(locals())
    
    return TrueSolarTime(
        value=apparent_solar_time,
        unit = MINUTES,
        timing_algorithm=SolarTimeModel.milne,
    )
