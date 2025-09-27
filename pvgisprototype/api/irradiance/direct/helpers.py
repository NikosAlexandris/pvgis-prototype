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
from numpy import ndarray
from pandas import DatetimeIndex

from pvgisprototype.constants import LOG_LEVEL_DEFAULT, VERBOSE_LEVEL_DEFAULT
from pvgisprototype.log import log_function_call


@log_function_call
def compare_temporal_resolution(
    timestamps: DatetimeIndex = None,
    array: ndarray = None,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> None:
    """
    Check if the frequency of `timestamps` matches the temporal resolution of the `array`.

    Parameters
    ----------
    timestamps:
        An array of generated timestamps.
    array:
        An array of data corresponding to some time series.

    Raises
    ------
        ValueError: If the lengths of the timestamps and data_series don't match.
    """
    if timestamps.size != array.size:
        raise ValueError(
            f"The frequency of `timestamps` ({timestamps.size}) does not match the temporal resolution of the `array` ({array.size}). Please ensure they have the same temporal resolution."
        )
