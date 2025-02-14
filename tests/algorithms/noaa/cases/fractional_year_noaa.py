from pydantic import ValidationError

from .cases_fractional_year import cases, cases_ids

cases_fractional_year_noaa = cases
cases_fractional_year_noaa_ids = cases_ids

# EXTRA INPUT NOT OK

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