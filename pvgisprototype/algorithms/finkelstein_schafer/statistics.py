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
from xarray import Dataset, DataArray
from pvgisprototype.algorithms.finkelstein_schafer.univariate_statistics import (
    calculate_daily_univariate_statistics,
)
from pvgisprototype.algorithms.finkelstein_schafer.cumulative_distribution import (
    calculate_yearly_monthly_ecdfs,
    calculate_long_term_monthly_ecdfs,
)



@log_function_call
def align_and_broadcast(data_array, reference_array):
    """Expand dimensions and broadcast a data array to match the structure of a
    template array.

    Parameters
    ----------
    data_array: xarray.DataArray
        The data array that needs to be aligned and broadcasted.
    template_array: xarray.DataArray
        The array providing the structure to which data_array should be aligned.

    Returns
    -------
    xarray.DataArray: The broadcasted data array with the same structure as the
    template_array.

    """
    return data_array.expand_dims(year=reference_array.year).broadcast_like(
        reference_array
    )


@log_function_call
def calculate_finkelstein_schafer_statistics(
    location_series_data_array: DataArray | Dataset,
) -> tuple[DataArray, Dataset, DataArray, DataArray]:
    """
    Calculate Finkelstein-Schafer statistics for typical meteorological year
    selection.

    The Finkelstein-Schafer (FS) statistic quantifies how well a candidate
    month represents the long-term climate by comparing its cumulative
    distribution function (CDF) to the multi-year average CDF. Lower FS values
    indicate months that are more representative of typical conditions.

    This implementation follows the ISO 15927-4:2005 standard for determining 
    typical meteorological data and the methodology described in Hall et al.
    (1978) [1]_.

    Algorithm
    ---------
    The Finkelstein-Schafer statistic is computed through the following steps:

    1. **Daily aggregation**: Calculate daily mean values from sub-daily 
       (e.g., hourly) time series data.

    2. **Long-term CDF**: For each calendar month *m*, compute the empirical 
       cumulative distribution function :math:`\\phi(q, m)` using daily values 
       aggregated across all years in the dataset.

    3. **Yearly CDFs**: For each calendar month *m* and year *y* for a quantity
       *q*, compute the empirical cumulative distribution function
       :math:`F(q, m, y)` using only the daily values from that specific month
       and year.

    4. **Finkelstein-Schafer statistic**: For each month *m* and year *y* for a
       quantity *q*, calculate the Finkelstein-Schafer statistic by integrating
       the absolute difference between the yearly and long-term CDFs:

       .. math::

           FS(q, m, y) = \\sum_{i} |F(q_i, m, y) - \\phi(q_i, m)|

       where the summation is over all quantile values :math:`q_i` in the
       distribution.

    5. **Ranking**: For each calendar month *m* for the quantity *q*, candidate
       months from different years are ranked by increasing Finkelstein-Schafer
       statistic FS(q, m, y). Lower values indicate months that better
       represent typical conditions.

    Parameters
    ----------
    location_series_data_array : DataArray or Dataset
        Time series meteorological data with a temporal dimension (typically
        hourly or sub-daily resolution). The data should span multiple years to
        enable meaningful long-term statistics. Acceptable formats include:
        
        - ``xarray.DataArray``: Single variable time series
        - ``xarray.Dataset``: Multi-variable time series
        
        The time coordinate should be datetime-like and parseable by pandas.

    Returns
    -------
    finkelstein_schafer_statistic : xarray.DataArray
        The computed Finkelstein-Schafer statistic with dimensions ``(month,
        year)``, where:
        
        - ``month``: Calendar month (1-12)
        - ``year``: Individual years in the input dataset
        
        Lower values indicate months that better represent long-term typical
        conditions.
        
    daily_statistics : xarray.Dataset
        Daily aggregated statistics including mean, min, max, and std computed
        from the input time series. Contains dimensions ``(time,)`` where time
        represents daily timestamps.
        
    yearly_monthly_ecdfs : xarray.DataArray
        Empirical cumulative distribution functions for each individual
        month-year combination. Dimensions: ``(month, year, quantile)``.
        
    long_term_monthly_ecdfs : xarray.DataArray
        Long-term empirical cumulative distribution functions computed across
        all years for each calendar month. Dimensions: ``(month, quantile)``.

    Notes
    -----
    The Finkelstein-Schafer statistic is a non-parametric measure that:
    
    - Does **not** assume any particular distribution shape (e.g., normal,
      uniform) Accounts for the **entire distribution**, not just central
      tendency (mean/median)
    - Is robust to outliers and extreme values
    - Enables objective selection of typical months based on distributional
      similarity
    
    **Typical use case**: This function is the core computational step in
    generating Typical Meteorological Year (TMY) datasets. After computing FS
    statistics for multiple meteorological variables (temperature, irradiance,
    humidity, wind speed), a weighted sum across variables is used to select
    the most representative month for each calendar month position in the TMY.

    **Data requirements**:
    
    - Minimum 5-10 years of data recommended for stable statistics
    - Complete or near-complete temporal coverage (missing data impacts CDF
      accuracy)
    - Sub-daily resolution (hourly preferred) to capture diurnal patterns

    References
    ----------
    .. [1] Hall, I. J., Prairie, R. R., Anderson, H. E., & Boes, E. C. (1978). 
           "Generation of a Typical Meteorological Year." Proceedings of the
           1978 Annual Meeting of the American Section of the International
           Solar Energy Society (AS/ISES), Denver, CO.
    
    .. [2] ISO 15927-4:2005. "Hygrothermal performance of buildings -
           Calculation and presentation of climatic data - Part 4: Hourly data
           for assessing the annual energy use for heating and cooling."
    
    .. [3] Wilcox, S., & Marion, W. (2008). "Users Manual for TMY3 Data Sets." 
           Technical Report NREL/TP-581-43156, National Renewable Energy
           Laboratory.

    Examples
    --------
    >>> import xarray as xr
    >>> import numpy as np
    >>> import pandas as pd
    >>> from pvgisprototype.algorithms.finkelstein_schafer.statistics import (
    ...     calculate_finkelstein_schafer_statistics
    ... )
    >>> 
    >>> # Create sample hourly temperature data for 3 years
    >>> time = pd.date_range('2015-01-01', '2017-12-31 23:00', freq='H')
    >>> temperature = 15 + 10 * np.sin(2 * np.pi * np.arange(len(time)) / (365.25 * 24))
    >>> temperature += np.random.normal(0, 2, len(time))  # Add noise
    >>> 
    >>> data = xr.DataArray(
    ...     temperature,
    ...     coords={'time': time},
    ...     dims=['time'],
    ...     name='temperature'
    ... )
    >>> 
    >>> # Calculate Finkelstein-Schafer statistics
    >>> fs_statistics, daily_statistics, yearly_ecdfs, long_term_ecdfs = (
    ...     calculate_finkelstein_schafer_statistics(data)
    ... )
    >>> 
    >>> # Find the most representative January across all years
    >>> january_fs = fs_stat.sel(month=1)
    >>> best_january_year = january_fs.idxmin(dim='year').values
    >>> print(f"Most typical January: {best_january_year}")  # doctest: +SKIP
    >>> print(f"FS statistic: {january_fs.min().values:.3f}")  # doctest: +SKIP

    See Also
    --------
    - calculate_daily_univariate_statistics() : Compute daily statistics from sub-daily data
    - calculate_yearly_monthly_ecdfs() : Compute yearly-monthly empirical CDFs
    - calculate_long_term_monthly_ecdfs() : Compute long-term monthly empirical CDFs
    - align_and_broadcast() : Align arrays for element-wise operations
    """
    # 1. Calculate daily means from hourly values
    daily_statistics = calculate_daily_univariate_statistics(
        data_array=location_series_data_array,
    )

    # 2. Calculate yearly-monthly ECDFs: F(q, m, y)
    yearly_monthly_ecdfs = calculate_yearly_monthly_ecdfs(
        dataset=daily_statistics,
        variable="mean",
    )

    # 3. Calculate long-term monthly ECDFs: φ(q, m)
    long_term_monthly_ecdfs = calculate_long_term_monthly_ecdfs(
        dataset=daily_statistics,
        variable="mean",
    )

    # 4. Align long-term ECDFs to yearly-monthly structure for subtraction
    aligned_long_term_monthly_ecdfs = align_and_broadcast(
        long_term_monthly_ecdfs, yearly_monthly_ecdfs
    )

    # 5. Calculate FS statistic: ∑|F(q,m,y) - φ(q,m)|
    finkelstein_schafer_statistic = abs(
        yearly_monthly_ecdfs - aligned_long_term_monthly_ecdfs
    ).sum(dim="quantile")

    return (
        finkelstein_schafer_statistic,
        daily_statistics,
        yearly_monthly_ecdfs,
        long_term_monthly_ecdfs,
    )
