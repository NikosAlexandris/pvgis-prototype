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
from numpy.typing import NDArray
from sparklines import sparklines
from pandas import DatetimeIndex, Timestamp, Series


def convert_series_to_sparkline(
    series: NDArray,
    timestamps: DatetimeIndex | Timestamp,
    frequency: str,
):
    """ """
    pandas_series = Series(series, timestamps)
    if (
        frequency == "SINGLE"
        or (isinstance(timestamps, DatetimeIndex) and timestamps.size == 1)
        or isinstance(timestamps, Timestamp)
    ):
        return "▁"  # Return a flat line for a single value
    
    yearly_sum_series = pandas_series.resample(frequency).sum()
    maximum=None
    if yearly_sum_series.all() == 0:
        maximum=1
    sparkline = sparklines(yearly_sum_series, maximum=maximum)[0]
    
    return sparkline
