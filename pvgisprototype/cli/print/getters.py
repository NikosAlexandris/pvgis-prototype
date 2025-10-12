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
        default: str | None = None,
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
