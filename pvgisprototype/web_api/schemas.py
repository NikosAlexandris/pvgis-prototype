from enum import Enum




class Timezone(str, Enum):
    GMT = "Etc/GMT"
    GMT_PLUS_0 = "Etc/GMT+0"
    GMT_PLUS_1 = "Etc/GMT+1"
    GMT_PLUS_10 = "Etc/GMT+10"
    GMT_PLUS_11 = "Etc/GMT+11"
    GMT_PLUS_12 = "Etc/GMT+12"
    GMT_PLUS_2 = "Etc/GMT+2"
    GMT_PLUS_3 = "Etc/GMT+3"
    GMT_PLUS_4 = "Etc/GMT+4"
    GMT_PLUS_5 = "Etc/GMT+5"
    GMT_PLUS_6 = "Etc/GMT+6"
    GMT_PLUS_7 = "Etc/GMT+7"
    GMT_PLUS_8 = "Etc/GMT+8"
    GMT_PLUS_9 = "Etc/GMT+9"
    GMT_MINUS_0 = "Etc/GMT-0"
    GMT_MINUS_1 = "Etc/GMT-1"
    GMT_MINUS_10 = "Etc/GMT-10"
    GMT_MINUS_11 = "Etc/GMT-11"
    GMT_MINUS_12 = "Etc/GMT-12"
    GMT_MINUS_13 = "Etc/GMT-13"
    GMT_MINUS_14 = "Etc/GMT-14"
    GMT_MINUS_2 = "Etc/GMT-2"
    GMT_MINUS_3 = "Etc/GMT-3"
    GMT_MINUS_4 = "Etc/GMT-4"
    GMT_MINUS_5 = "Etc/GMT-5"
    GMT_MINUS_6 = "Etc/GMT-6"
    GMT_MINUS_7 = "Etc/GMT-7"
    GMT_MINUS_9 = "Etc/GMT-9"
    GMT0 = "Etc/GMT0"
    GREENWICH = "Etc/Greenwich"
    UCT = "Etc/UCT"
    UTC = "UTC"
    UNIVERSAL = "Universal"


class AnalysisLevel(str, Enum):
    Minimal = 'Minimal'
    Simple = 'Simple'
    Advanced = 'Advanced'
    Extended = 'Extended'
    NoneValue = 'None'


class Frequency(str, Enum):
    Yearly = "Yearly"
    Seasonal = "Seasonal"
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
