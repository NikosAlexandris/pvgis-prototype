from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype import Longitude
from pvgisprototype import Latitude


"""
Test cases for the Solar Azimuth

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
        0 <= expected <= 2*pi)
         
    if angle_output_units == 'degrees':
        0 <= expected <= 360)
"""


cases_for_solar_azimuth = [
    (
        Longitude(value=0.5585053606381855, unit='radians'),
        Latitude(value=0.47123889803846897, unit='radians'),
        datetime(2024, 9, 4, 7, 32),
        ZoneInfo('UTC'),
        'radians',
        2.45701,
    ),
    (
        Longitude(value=32, unit='degrees'),
        Latitude(value=27, unit='degrees'),
        datetime(2024, 9, 4, 7, 32),
        ZoneInfo('UTC'),
        'degrees',
        141.01435,
    ),
]


