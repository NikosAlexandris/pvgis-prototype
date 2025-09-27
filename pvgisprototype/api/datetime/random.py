#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
"""
Helper functions to generate random timestamps
"""

from calendar import monthrange
from datetime import datetime
from random import choice, randint
from zoneinfo import ZoneInfo, available_timezones


def random_day_of_year(days_in_year: int) -> int:
    """
    Generate a random datetime and timezone object
    """
    return randint(1, days_in_year)


def random_datetimezone() -> tuple:
    """
    Generate a random datetime and timezone object
    """
    year = datetime.now().year
    month = randint(1, 12)
    _, days_in_month = monthrange(year, month)
    day = randint(1, days_in_month)
    hour = randint(0, 23)
    minute = randint(0, 59)
    second = randint(0, 59)
    datetimestamp = datetime(
        year, month, day, hour, minute, second, tzinfo=ZoneInfo("UTC")
    )
    timezone_str = choice(list(available_timezones()))
    timezone = ZoneInfo(timezone_str)

    return datetimestamp, timezone
