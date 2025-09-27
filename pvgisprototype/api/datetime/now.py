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
from datetime import datetime
from zoneinfo import ZoneInfo


def now_datetime() -> datetime:
    """Returns the current datetime in UTC.

    Return an aware timestamp using the local system time, however defaulting
    to UTC timezone.
    """
    return datetime.now()


def now_local_datetimezone():
    """Get current local date and time and zone"""
    print("[yellow]i[/yellow] Runnning the now_local_datetimezone() function!")
    return datetime.now().astimezone()


# Timezone


def now_utc_datetimezone() -> datetime:
    """Returns the current datetime in UTC.

    Return an aware timestamp using the local system time, however defaulting
    to UTC timezone.
    """
    return datetime.now(ZoneInfo("UTC"))
