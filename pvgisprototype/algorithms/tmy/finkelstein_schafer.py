from pvgisprototype.algorithms.tmy.models import LONG_TERM_MONTHLY_ECDFs_COLUMN_NAME, YEARLY_MONTHLY_ECDFs_COLUMN_NAME
from pvgisprototype.log import log_function_call
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import NEIGHBOR_LOOKUP_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT
from xarray import Dataset
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
    """Calculate daily max, min, and mean for each variable in the dataset."""
    # Resample data to daily frequency
    resampled_data = data_array.resample(time='1D')
    
    daily_max = resampled_data.max(dim='time', skipna=True)
    daily_min = resampled_data.min(dim='time', skipna=True)
    daily_mean = resampled_data.mean(dim='time', skipna=True)

    result = Dataset({
        'max': daily_max,
        'min': daily_min,
        'mean': daily_mean
    })

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
    # yearly_monthly_cdfs,
    # long_term_monthly_cdfs,
    time_series,
    meteorological_variable: MeteorologicalVariable,
    longitude: float,
    latitude: float,
    timestamps: Timestamp | DatetimeIndex = Timestamp.now(),
    start_time: datetime | None = None,  # Used by a callback function
    periods: int | None = None,  # Used by a callback function
    frequency: str | None = None,  # Used by a callback function
    end_time: datetime | None = None,  # Used by a callback function
    variable_name_as_suffix: bool = True,
    neighbor_lookup: MethodForInexactMatches = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: float | None = TOLERANCE_DEFAULT,
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
    weighting_scheme: TypicalMeteorologicalMonthWeightingScheme = TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
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
    
    """
    # 1. Read hourly time series
    location_series_data_array = select_time_series(
        time_series=time_series,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        # convert_longitude_360=convert_longitude_360,
        mask_and_scale=mask_and_scale,  # True ?
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        variable_name_as_suffix=variable_name_as_suffix,
        verbose=verbose,
    )

    # 2
    daily_statistics = calculate_daily_univariate_statistics(
            data_array=location_series_data_array,
    )

    # 3
    yearly_monthly_ecdfs = calculate_yearly_monthly_ecdfs(
            dataset=daily_statistics,
            variable='mean',
    )

    # 4
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
