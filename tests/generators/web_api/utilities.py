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
import random
from datetime import timedelta
from zoneinfo import ZoneInfo
from pandas import Timestamp
from pytz import NonExistentTimeError, AmbiguousTimeError

from pvgisprototype.constants import TIMEZONE_UTC


def validate_time(datetime_object, timezone):
    """Check if a datetime is valid in the given timezone."""
    try:
        localized = Timestamp(datetime_object, tz=ZoneInfo(timezone))
        localized.tz_convert(ZoneInfo(TIMEZONE_UTC)).tz_localize(None)
    except (NonExistentTimeError, AmbiguousTimeError):
        return False

    return True

def generate_random_date_pair(start, end):
    """Generate a random start_date and end_date such that start_date < end_date."""
    start_date = start + timedelta(days=random.randint(0, (end - start).days))

    if start_date >= end:
        return start_date, start_date + timedelta(days=1)

    end_date = start_date + timedelta(days=random.randint(1, (end - start_date).days))
    return start_date.strftime('%Y/%m/%d'), end_date.strftime('%Y/%m/%d')


def remove_none_values(parameters):
    """Remove keys with None values from the parameters dictionary."""
    return {key: value for key, value in parameters.items() if value is not None}