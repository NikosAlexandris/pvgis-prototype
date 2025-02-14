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
