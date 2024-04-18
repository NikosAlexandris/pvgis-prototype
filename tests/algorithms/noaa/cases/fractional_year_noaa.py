from datetime import datetime
from pandas import Timestamp
from pandas import DatetimeIndex
from numpy import array as numpy_array
from pydantic import ValidationError

from pvgisprototype.constants import RADIANS
from pvgisprototype import FractionalYear
from pvgisprototype.api.utilities.timestamp import generate_datetime_series


# INPUT OK

year=2010
month=6
day=21
hour=12
fractional_year_noaa=2.9436293

timestamp_string='2010-06-21 12:00:00'

start_time="2010-06-21 12:00:00"
end_time="2010-06-21 13:00:00"
frequency = "h"
output_series_1=2.9436293
output_series_2=2.9443464

cases_fractional_year_noaa = [
    ({"timestamps": DatetimeIndex([Timestamp(year=year, month=month, day=day, hour=hour)])}, FractionalYear(value=numpy_array([fractional_year_noaa], dtype='float32'), unit=RADIANS)),
    ({"timestamps": DatetimeIndex([Timestamp(timestamp_string)])}, FractionalYear(value=numpy_array([2.935022], dtype='float32'), unit=RADIANS)),
    ({"timestamps": generate_datetime_series(start_time=start_time, end_time=end_time, frequency=frequency)}, FractionalYear(value=numpy_array([output_series_1, output_series_2], dtype='float32'), unit=RADIANS)),
    ]

cases_fractional_year_noaa_ids = [
    f"Timestamp from Y-M-D:H: {year}-{month}-{day}:{hour}->{fractional_year_noaa:.3f}",
    f"Timestamp from string: {timestamp_string}->{fractional_year_noaa:.3f}",
    f"Datetime series hourly from {start_time}-{end_time}->{output_series_1:.3f}, {output_series_2:.3f}",
]

# INPUT NOT OK

string_datetime = "2020-01-01:12:00:00"
random_number = 34.223424252423
cases_fractional_year_noaa_invalid = [
    ({"timestamps": string_datetime}, ValidationError),
    ({"timestamps": random_number}, ValidationError),
]

cases_fractional_year_noaa_invalid_ids = [
    f"Timestamp from string: {string_datetime}->{ValidationError}",
    f"Timestamp from random number: {random_number:.2f}->{ValidationError}",
]