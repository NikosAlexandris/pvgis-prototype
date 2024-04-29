from pydantic import ValidationError

from .cases_equation_of_time import cases
from .cases_equation_of_time import cases_ids

cases_equation_of_time_noaa = cases

cases_equation_of_time_noaa_ids = cases_ids

# INPUT NOT OK

string_datetime = "2020-01-01:12:00:00"
random_number = 34.223424252423
cases_equation_of_time_noaa_invalid = [
    ({"timestamps": string_datetime}, ValidationError),
    ({"timestamps": random_number}, ValidationError),
]

cases_equation_of_time_noaa_invalid_ids = [
    f"Timestamp from string: {string_datetime}->{ValidationError}",
    f"Timestamp from random number: {random_number:.2f}->{ValidationError}",
]