from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype import Longitude
from pvgisprototype import Latitude


"""
Test cases for the Solar Declination

- timestamp: an input `timestamp` represented via a `datetime` object,
  for example, the date-time 2023-07-25 at 12:00 may be built as follows:

    (datetime(year=2023, month=7, day=25, hour=12)

- timezone:

    ZoneInfo('UTC')

- angle_output_units:

    'radians'

- expected: the expected output value for the given input:

    if angle_output_units == 'radians':
        0 <= expected <= 2*pi)
         
    if angle_output_units == 'degrees':
        0 <= expected <= 360)
"""


cases_for_solar_declination = [
    (
        datetime(2021, 10, 21, 10, 00),
        'radians',
        -0.18179,
    ),
    (
        datetime(2021, 10, 21, 10, 00),
        'degrees',
        -10.41568,
    ),
]


