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
from pvgisprototype.algorithms.tmy.models import LONG_TERM_MONTHLY_ECDFs_COLUMN_NAME, YEARLY_MONTHLY_ECDFs_COLUMN_NAME
from pvgisprototype.log import log_function_call
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import NEIGHBOR_LOOKUP_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT
from xarray import Dataset, DataArray
from pandas import DatetimeIndex, Timestamp
from datetime import datetime
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.algorithms.tmy.weighting_scheme_model import MeteorologicalVariable, TypicalMeteorologicalMonthWeightingScheme
from pvgisprototype.algorithms.tmy.weighting_scheme_model import TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.algorithms.tmy.cumulative_distribution import calculate_yearly_monthly_ecdfs, calculate_long_term_monthly_ecdfs
from pvgisprototype.algorithms.tmy.weighting_scheme_model import get_typical_meteorological_month_weighting_scheme
from pvgisprototype.constants import (
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
)
from devtools import debug
from pathlib import Path
from pvgisprototype.algorithms.tmy.finkelstein_schafer import calculate_weighted_finkelstein_schafer_statistics


@log_function_call
def model_weighted_finkelstein_schafer_statistics(
    time_series: Path | DataArray | Dataset,
    meteorological_variable: MeteorologicalVariable,
    longitude: float,
    latitude: float,
    timestamps: Timestamp | DatetimeIndex = Timestamp.now(),
    start_time: datetime | None = None,
    periods: int | None = None,
    frequency: str | None = None,
    end_time: datetime | None = None,
    variable_name_as_suffix: bool = True,
    neighbor_lookup: MethodForInexactMatches = NEIGHBOR_LOOKUP_DEFAULT, # type: ignore[assignment]
    tolerance: float | None = TOLERANCE_DEFAULT,
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
    weighting_scheme: TypicalMeteorologicalMonthWeightingScheme = TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT, # type: ignore[assignment]
    verbose: int = VERBOSE_LEVEL_DEFAULT,
)->dict:
    """Wrapper API function for calculating Finkelstein-Schafer statistics.

    Parameters
    ----------
    time_series : Path | DataArray | Dataset
        Time series data as a path, or xarray read object
    meteorological_variable : MeteorologicalVariable
        Meteorological variable to calculate TMY
    longitude : float
        Longitude of the selected location
    latitude : float
        Latitude of the selected location
    timestamps : Timestamp | DatetimeIndex, optional
        Timestamps to perform calculations, by default Timestamp.now()
    start_time : datetime | None, optional
        Start timestamp, by default None
    periods : int | None, optional
        Number of Periods to generate, by default None
    frequency : str | None, optional
        Frequency for the generation of timestamps given either 1) a start_time and end_time or 2) start_time plus periods _or 3) end_time plus the periods. See also relevant notes in Pandas documentation, by default None
    end_time : datetime | None, optional
        End Timestamp, by default None
    variable_name_as_suffix : bool, optional
        Add variable name as suffix, by default True
    neighbor_lookup : MethodForInexactMatches, optional
        Enable nearest neighbor (inexact) lookups. Read Xarray manual on nearest-neighbor-lookups, by default NEIGHBOR_LOOKUP_DEFAULT
    mask_and_scale : bool, optional
        Mask and scale the series, by default MASK_AND_SCALE_FLAG_DEFAULT
    in_memory : bool, optional
        Whether to process data in memory, by default IN_MEMORY_FLAG_DEFAULT
    weighting_scheme : TypicalMeteorologicalMonthWeightingScheme, optional
        Weighting scheme for the calculation of weights, by default TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT

    Returns
    -------
    dict
        Results in a dictionary including metadata, Finkelstein-Schafer statistic, CDFs and daily statistics
    """

    if isinstance(time_series, DataArray | Dataset):
        location_series_data_array = time_series
    else:
        location_series_data_array = select_time_series(
            time_series=time_series,
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            start_time=start_time,
            end_time=end_time,
            mask_and_scale=mask_and_scale,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            in_memory=in_memory,
            variable_name_as_suffix=variable_name_as_suffix,
            verbose=verbose,
        )
    
    finkelstein_schafer_statistics = calculate_weighted_finkelstein_schafer_statistics(
        location_series_data_array=location_series_data_array,
        meteorological_variable=meteorological_variable,
        weighting_scheme=weighting_scheme,
        verbose=verbose,
    )

    return finkelstein_schafer_statistics
