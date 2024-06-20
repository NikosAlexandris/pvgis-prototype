from enum import Enum

#from pvgisprototype.web_api.utilities import get_timezones
# Timezone = Enum('Timezone', {tz: tz for tz in get_timezones()}) # FIXME Add later when all timezones work properly


class Timezone(Enum):
    ETC_GMT = "Etc/GMT"
    ETC_GMT_PLUS_0 = "Etc/GMT+0"
    ETC_GMT_PLUS_1 = "Etc/GMT+1"
    ETC_GMT_PLUS_10 = "Etc/GMT+10"
    ETC_GMT_PLUS_11 = "Etc/GMT+11"
    ETC_GMT_PLUS_12 = "Etc/GMT+12"
    ETC_GMT_PLUS_2 = "Etc/GMT+2"
    ETC_GMT_PLUS_3 = "Etc/GMT+3"
    ETC_GMT_PLUS_4 = "Etc/GMT+4"
    ETC_GMT_PLUS_5 = "Etc/GMT+5"
    ETC_GMT_PLUS_6 = "Etc/GMT+6"
    ETC_GMT_PLUS_7 = "Etc/GMT+7"
    ETC_GMT_PLUS_8 = "Etc/GMT+8"
    ETC_GMT_PLUS_9 = "Etc/GMT+9"
    ETC_GMT_MINUS_0 = "Etc/GMT-0"
    ETC_GMT_MINUS_1 = "Etc/GMT-1"
    ETC_GMT_MINUS_10 = "Etc/GMT-10"
    ETC_GMT_MINUS_11 = "Etc/GMT-11"
    ETC_GMT_MINUS_12 = "Etc/GMT-12"
    ETC_GMT_MINUS_13 = "Etc/GMT-13"
    ETC_GMT_MINUS_14 = "Etc/GMT-14"
    ETC_GMT_MINUS_2 = "Etc/GMT-2"
    ETC_GMT_MINUS_3 = "Etc/GMT-3"
    ETC_GMT_MINUS_4 = "Etc/GMT-4"
    ETC_GMT_MINUS_5 = "Etc/GMT-5"
    ETC_GMT_MINUS_6 = "Etc/GMT-6"
    ETC_GMT_MINUS_7 = "Etc/GMT-7"
    ETC_GMT_MINUS_9 = "Etc/GMT-9"
    ETC_GMT0 = "Etc/GMT0"
    ETC_GREENWICH = "Etc/Greenwich"
    ETC_UCT = "Etc/UCT"
    ETC_UTC = "Etc/UTC"
    ETC_UNIVERSAL = "Etc/Universal"
    UTC = "UTC"
    UNIVERSAL = "Universal"


class Frequency(Enum):
    Year = "Year"  # FIXME Does not seem to work
    Season = "Season"  # FIXME Does not seem to work
    Month = "Month"  # FIXME Does not seem to work
    Week = "Week"  # FIXME Does not seem to work
    Day = "Day"  # FIXME Does not seem to work
    Hour = "Hour"  # Works properly


class GroupBy(Enum):
    Yearly = "Yearly"
    Seasonal = "Seasonal"
    Monthly = "Monthly"
    Weekly = "Weekly"
    Daily = "Daily"
    Hourly = "Hourly"
    N = "Do not group by"


class AngleOutputUnit(Enum):
    RADIANS = "Radians"
    DEGREES = "Degrees"
