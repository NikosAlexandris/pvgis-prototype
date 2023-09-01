from datetime import datetime

"""
Test cases for the Equation of Time

- timestamp: an input `timestamp` represented via a `datetime` object,
  for example, the date-time 2023-07-25 at 12:00 may be built as follows:

    (datetime(year=2023, month=7, day=25, hour=12)

- time_output_units: the unit for the expected output value, for example the
  string

    'minutes'

- expected: the expected output value for the given input `timestamp`, for
  example, the minutes for the date 2023-07-25 at 12:00 are expected to be:

    14.25
"""
cases_for_equation_of_time = [
    (datetime(year=2023, month=7, day=25, hour=12), "minutes", 14.25),
    (datetime(year=2023, month=12, day=21, hour=12), "minutes", -3.44),
    (datetime(year=2023, month=1, day=1, hour=12), "minutes", -3.99),
    (datetime(year=2023, month=6, day=21, hour=12), "minutes", 1.87),
    (datetime(year=2023, month=7, day=25, hour=12), "minutes", -6.54),
    (datetime(year=2023, month=12, day=21, hour=12), "minutes", 2.17),
    (datetime(year=2023, month=1, day=1, hour=12), "minutes", -2.9),
    (datetime(year=2023, month=6, day=21, hour=12), "minutes", -1.33),
]
