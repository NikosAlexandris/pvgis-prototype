from pandas import isna, DatetimeIndex
from numpy import ndarray
from pvgisprototype.api.position.models import SolarPositionParameter
from pvgisprototype.constants import NOT_AVAILABLE


def get_scalar(value, index, places):
    """Safely get a scalar value from an array or return the value itself"""
    if isinstance(value, ndarray):
        if value.size > 1:
            return value[index]
        else:
            return value[0]

    return value


def get_value_or_default(
        dictionary: dict,
        key: str,
        default: str | None = NOT_AVAILABLE
):
    """Get a value from a dictionary or return a default value"""
    if dictionary is not None:
        return dictionary.get(key, default)
    else:
        return None


def get_event_time_value(
        dictionary,
        idx,
        rounding_places,
):
    """Safely get the event time """
    if dictionary is not None:
        event_time_series = get_value_or_default(
            dictionary=dictionary,
            key=SolarPositionParameter.event_time,
            default=None,
            )
        if event_time_series is not None and not (
            isinstance(event_time_series, DatetimeIndex) and
            all(isna(x) for x in event_time_series)
        ):
            return get_scalar(event_time_series, idx, rounding_places)
    else:
        return None
