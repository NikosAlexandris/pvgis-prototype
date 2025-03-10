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


@log_function_call
def calculate_daily_univariate_statistics(data_array):
    """
    Calculate daily max, min, and mean for each variable in the dataset using pandas.
    """
    # Convert xarray DataArray to pandas DataFrame
    df = data_array.to_dataframe(name="value")

    # Resample to daily frequency
    daily_stats = df.resample("1D").agg(["max", "min", "mean"])

    # Convert pandas DataFrame back to xarray Dataset
    result = Dataset(
        {
            "max": (["time"], daily_stats["value"]["max"].values),
            "min": (["time"], daily_stats["value"]["min"].values),
            "mean": (["time"], daily_stats["value"]["mean"].values),
        },
        coords={"time": daily_stats.index},
    )

    return result


@log_function_call
def align_and_broadcast(data_array, reference_array):
    """Expand dimensions and broadcast a data array to match the structure of a template array.

    Parameters
    ----------
    data_array: xarray.DataArray
        The data array that needs to be aligned and broadcasted.
    template_array: xarray.DataArray
        The array providing the structure to which data_array should be aligned.

    Returns
    -------
    xarray.DataArray: The broadcasted data array with the same structure as the template_array.

    """
    return data_array.expand_dims(year=reference_array.year).broadcast_like(reference_array)


@log_function_call
def calculate_finkelstein_schafer_statistics(
    location_series_data_array: DataArray | Dataset,
):
    """Calculate the Finkelstein-Schafer statistic for a meteorological
    variable.

    Calculate the Finkelstein-Schafer statistic for a meteorological variable
    via the following algorithm :

        1. Calculate the daily means from the hourly values.

        2. For each month 𝑚 of the quantity 𝑞, calculate the cumulative
        distribution function 𝜙(𝑞,𝑚) using the daily values for all years.
        
        3. For each year 𝑦 and each month 𝑚 of the quantity 𝑞, calculate the
        cumulative distribution function 𝐹(𝑞,𝑚,𝑦) using the daily values
        for that year.
        
        4. For each month 𝑚 and each year 𝑦 of the quantity 𝑞, calculate the
        Finkelstein–Schafer statistic, summing over the range of the
        distribution values:

            𝐹𝑆(𝑞,𝑚,𝑦) = ∑|𝐹(𝑞,𝑚,𝑦) − 𝜙(𝑞,𝑚,𝑦)|.  Equation (1) in [1]_
        
        5. For each month 𝑚 of the quantity 𝑞, rank the the individual months
        in the multi-year period in order of increasing 𝐹𝑆(𝑞,𝑚,𝑦).
    
    Parameters
    ----------
    location_series_data_array : DataArray | Dataset
        Time series data as a xarray read object
    """
    # 1
    daily_statistics = calculate_daily_univariate_statistics(
            data_array=location_series_data_array,
    )

    # 2
    yearly_monthly_ecdfs = calculate_yearly_monthly_ecdfs(
            dataset=daily_statistics,
            variable='mean',
    )

    # 3
    long_term_monthly_ecdfs = calculate_long_term_monthly_ecdfs(
            dataset=daily_statistics,
            variable='mean',
    )
    
    # align to yearly_monthly_ecdfs to enable subtraction
    aligned_long_term_monthly_ecdfs = align_and_broadcast(
        long_term_monthly_ecdfs, yearly_monthly_ecdfs
    )

    # 5
    finkelstein_schafer_statistic = abs(
        yearly_monthly_ecdfs - aligned_long_term_monthly_ecdfs
    ).sum(dim="quantile")

    return finkelstein_schafer_statistic, daily_statistics, yearly_monthly_ecdfs, long_term_monthly_ecdfs

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

    finkelstein_schafer_statistic, daily_statistics, yearly_monthly_ecdfs, long_term_monthly_ecdfs = calculate_finkelstein_schafer_statistics(location_series_data_array)

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
