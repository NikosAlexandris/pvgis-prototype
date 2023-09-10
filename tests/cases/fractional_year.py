from datetime import datetime
from math import pi


tolerances = [1, 0.1]

# Input for the _simple_ function

cases_for_fractional_year = [
    (datetime(year=2023, month=7, day=25, hour=12), 3.55),
    (datetime(year=2023, month=1, day=1, hour=0), 0),  # boundary case of 0
    (datetime(year=2023, month=12, day=31, hour=23), 2 * pi),  # boundary case of 2*pi
]

# Single element input lists for the time series function

timestamp_in_list = [
    [
        datetime(year=2023, month=7, day=25, hour=12),
    ],
    [
        datetime(year=2023, month=1, day=1, hour=0),  # boundary case of 0
    ],
    [
        datetime(year=2023, month=12, day=31, hour=23),  # boundary case of 2*pi
    ],
]
expected_fractional_year_in_list = [
    [3.55],
    [0],
    [2 * pi],
]
cases_for_fractional_year_series_single_timestamp = list(
    zip(timestamp_in_list, expected_fractional_year_in_list)
)


# Series input lists

timestamps = [
    [
        datetime(year=2023, month=7, day=25, hour=12),
        datetime(year=2023, month=1, day=1, hour=0),  # boundary case of 0
        datetime(year=2023, month=12, day=31, hour=23),  # boundary case of 2*pi
    ],
    [
        datetime(year=2022, month=3, day=20, hour=12),
        datetime(year=2022, month=6, day=21, hour=12),
    ],
]
expected_fractional_year_series = [
    [3.55, 0, 2 * pi],
    [1.34, 2.94],
]
cases_for_fractional_year_series = list(
    zip(timestamps, expected_fractional_year_series)
)
