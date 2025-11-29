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
from pvgisprototype.log import log_function_call
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from xarray import Dataset, DataArray
from pvgisprototype.algorithms.finkelstein_schafer.statistics import (
    calculate_finkelstein_schafer_statistics,
)
from pvgisprototype.api.tmy.weighting_scheme_model import (
    MeteorologicalVariable,
    TypicalMeteorologicalMonthWeightingScheme,
    TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT,
    get_typical_meteorological_month_weighting_scheme,
)
from pvgisprototype.api.tmy.models import (
    LONG_TERM_MONTHLY_ECDFs_COLUMN_NAME,
    YEARLY_MONTHLY_ECDFs_COLUMN_NAME,
)
from pvgisprototype.constants import (
    VERBOSE_LEVEL_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
)


@log_function_call
def calculate_weighted_finkelstein_schafer_statistics(
    location_series_data_array: DataArray | Dataset,
    meteorological_variable: MeteorologicalVariable,
    weighting_scheme: TypicalMeteorologicalMonthWeightingScheme = TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the weighted Finkelstein-Schafer statistic for a meteorological
    variable using a weighting scheme.

    Parameters
    ----------
    location_series_data_array : DataArray | Dataset
        Time series data as a xarray read object
    meteorological_variable : MeteorologicalVariable
        Meteorological variable to calculate TMY
    weighting_scheme : TypicalMeteorologicalMonthWeightingScheme, optional
        Weighting scheme for the calculation of weights, by default TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT
    
    Returns
    -------
    dict
        Results in a dictionary including metadata, Finkelstein-Schafer statistic, CDFs and daily statistics
    """
    (
        finkelstein_schafer_statistic,
        daily_statistics,
        yearly_monthly_ecdfs,
        long_term_monthly_ecdfs,
    ) = calculate_finkelstein_schafer_statistics(location_series_data_array)

    # Weighting as per alternative TMY algorithms
    typical_meteorological_month_weights = (
        get_typical_meteorological_month_weighting_scheme(
            weighting_scheme=weighting_scheme,
            meteorological_variable=meteorological_variable,
        )
    )
    weighted_finkelstein_schafer_statistic = finkelstein_schafer_statistic * typical_meteorological_month_weights
    ranked_finkelstein_schafer_statistic = weighted_finkelstein_schafer_statistic.rank(dim='year', keep_attrs=True)

    components_container = {
        "Metadata": lambda: {
        },
        "Finkelstein-Schafer statistic": lambda: {
            "Ranked": ranked_finkelstein_schafer_statistic,
            "Weighted": weighted_finkelstein_schafer_statistic,
            "Weights": typical_meteorological_month_weights,
            "Weighting scheme": weighting_scheme,
            "Weighting variable": meteorological_variable,
            "Finkelstein-Schafer": finkelstein_schafer_statistic,
        },
        "Cumulative Distribution": lambda: {
            LONG_TERM_MONTHLY_ECDFs_COLUMN_NAME: long_term_monthly_ecdfs,
            YEARLY_MONTHLY_ECDFs_COLUMN_NAME: yearly_monthly_ecdfs,
        },
        "Daily statistics": lambda: {
            "Daily statistics": daily_statistics,
        },
    }
    components = {}
    for _, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return components


@log_function_call
def model_weighted_finkelstein_schafer_statistics(
    time_series: DataArray | Dataset,
    meteorological_variable: MeteorologicalVariable,
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
    finkelstein_schafer_statistics = calculate_weighted_finkelstein_schafer_statistics(
        location_series_data_array=time_series,
        meteorological_variable=meteorological_variable,
        weighting_scheme=weighting_scheme,
        verbose=verbose,
    )

    return finkelstein_schafer_statistics
