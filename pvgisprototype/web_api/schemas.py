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
from enum import Enum
from pvgisprototype.web_api.utilities import get_timezones


class Timezone(str, Enum):
    # Using a dictionary comprehension to dynamically generate enum members
    _ignore_ = "names"  # Optional, to avoid creating a member for this variable
    names = {
        timezone.replace("/", "_").replace("-", "_"): timezone
        for timezone in get_timezones()
    }
    locals().update(names)


class AnalysisLevel(str, Enum):
    Minimal = "Minimal"
    Simple = "Simple"
    Advanced = "Advanced"
    Extended = "Extended"
    NoneValue = "None"


class Frequency(str, Enum):
    Yearly = "Yearly"
    Monthly = "Monthly"
    Weekly = "Weekly"
    Daily = "Daily"
    Hourly = "Hourly"
    Minutely = "Minutely"


class GroupBy(str, Enum):
    Yearly = "Yearly"
    Seasonal = "Seasonal"
    Monthly = "Monthly"
    Weekly = "Weekly"
    Daily = "Daily"
    Hourly = "Hourly"
    Minutely = "Minutely"
    NoneValue = "None"


class AngleOutputUnit(str, Enum):
    RADIANS = "Radians"
    DEGREES = "Degrees"
