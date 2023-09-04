from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype import Longitude
from pvgisprototype import Latitude


"""
Test cases for the Solar Altitude

- Longitude:

    Longitude(value=0.5, unit='radians')

- Latitude:

    Latitude(value=0.5, unit='radians')

- timestamp: an input `timestamp` represented via a `datetime` object,
  for example, the date-time 2023-07-25 at 12:00 may be built as follows:

    (datetime(year=2023, month=7, day=25, hour=12)

- timezone:

    ZoneInfo('UTC')

- angle_output_units:

    'radians'

- expected: the expected output value for the given input:

    if angle_output_units == 'radians':
        -pi/2 <= expected <= pi/2)
         
    if angle_output_units == 'degrees':
        -90 <= expected <= 90)
"""


cases_for_solar_altitude = [
    (
        Longitude(value=0.5585053606381855, unit='radians'),
        Latitude(value=0.47123889803846897, unit='radians'),
        datetime(2024, 9, 4, 7, 32),
        ZoneInfo('UTC'),
        'radians',
        0.91262,
    ),
    (
        Longitude(value=32, unit='degrees'),
        Latitude(value=27, unit='degrees'),
        datetime(2024, 9, 4, 7, 32),
        ZoneInfo('UTC'),
        'degrees',
        51.62890,
    ),
]


