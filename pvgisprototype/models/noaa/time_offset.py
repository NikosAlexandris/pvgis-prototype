from .noaa_models import CalculateTimeOffsetNOAAInput
from datetime import datetime
from .decorators import validate_with_pydantic
from math import pi
from .equation_of_time import calculate_equation_of_time_noaa
from typing import NamedTuple
from pvgisprototype.api.named_tuples import generate


radians_to_time_minutes = lambda value_in_radians: (1440 / (2 * pi)) * value_in_radians


@validate_with_pydantic(CalculateTimeOffsetNOAAInput)
def calculate_time_offset_noaa(
        longitude: float, 
        timestamp: datetime, 
        time_output_units: str = 'minutes',  # redesign me!
        angle_units: str = 'radians',
    ) -> NamedTuple:
    """Calculate the time offset for NOAA's solar position calculations
    measured in minutes.

    The time offset (in minutes) incorporates the Equation of Time and accounts
    for the variation of the Local Solar Time (LST) within a given time zone
    due to the longitude variations within the time zone.

    Parameters
    ----------
    timestamp: datetime
        The timestamp to calculate offset for
    longitude: float
        The longitude for calculation
    equation_of_time: float
        The equation of time value for calculation

    Returns
    -------
    float: The time offset

    Notes
    -----

    The reference equation here is:

        `time_offset = eqtime + 4*longitude – 60*timezone`

        (source: https://gml.noaa.gov/grad/solcalc/solareqns.PDF)

        where (variable name and units):
            - time_offset, minutes
            - longitude, degrees
            - timezone, hours
            - eqtime, minutes

    A cleaner (?) reference:

        `TC = 4 * (Longitude - LSTM) + EoT`

        where:
            - TC       : Time Correction Factor, minutes
            - Longitude: Geographical Longitude, degrees
            - LSTM     : Local Standard Time Meridian, degrees * hours

                where:
                - `LSTM = 15 degrees * ΔTUTC`
            
                    where:
                    - ΔTUTC = LT - UTC, hours

                        where:
                        - LT : Local Time
                        - UTC: Universal Coordinated Time
                        - difference of LT from UTC in hours

            - The factor of 4 minutes comes from the fact that the Earth
              rotates 1° every 4 minutes.

            Examples:
                Mount Olympus is UTC + 2, hence LSTM = 15 * 2 = 30 deg. East
    """
    longitude_in_minutes = radians_to_time_minutes(longitude)  # time
    timezone_offset_minutes = timestamp.utcoffset().total_seconds() / 60  # minutes
    equation_of_time = calculate_equation_of_time_noaa(timestamp,
                                                               time_output_units,
                                                               angle_units,
                                                               )  # minutes
    time_offset = longitude_in_minutes - timezone_offset_minutes + equation_of_time.value

    if not -720 <= time_offset <= 720:
        raise ValueError("The time offset must range within [-720, 720] minutes ?")

    time_offset = generate(
        'time_offset'.upper(),
        (time_offset, time_output_units)
    )
    return time_offset

