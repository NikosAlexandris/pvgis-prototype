"""
"""

from pvgisprototype.log import logger
from datetime import datetime
from pvgisprototype.api.utilities.timestamp import now_datetime
from pandas import DatetimeIndex
from typing import Optional
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.series.select import select_time_series
import xarray as xr
import numpy as np
import pandas as pd
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import NEIGHBOR_LOOKUP_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT


def calculate_daily_univariate_statistics(data_array):
    """Calculate daily max, min, and mean for each variable in the dataset."""
    # Resample data to daily frequency
    resampled_data = data_array.resample(time='1D')
    
    # Calculate max, min, and mean
    daily_max = resampled_data.max(dim='time', skipna=True)
    daily_min = resampled_data.min(dim='time', skipna=True)
    daily_mean = resampled_data.mean(dim='time', skipna=True)

    # Combine the results into a single Dataset for easier handling
    result = xr.Dataset({
        'max': daily_max,
        'min': daily_min,
        'mean': daily_mean
    })

    return result


def calculate_cdf(data_array):
    """Calculate the empirical cumulative distribution function (CDF) of the data, ensuring unique coordinates."""
    sorted_data = np.sort(data_array.values.flatten())
    unique_sorted_data = (
        sorted_data + np.random.rand(sorted_data.size) * 1e-10
    )  # Ensuring unique values by adding a small random noise; adjust the scale as needed for data sensitivity
    cdf = np.arange(1, unique_sorted_data.size + 1) / unique_sorted_data.size
    return xr.DataArray(cdf, coords=[unique_sorted_data], dims=["sorted_values"])


def calculate_monthly_cdfs(data_array):
    """Calculate monthly CDFs for each variable for each month and year."""
    return data_array.groupby('time.month').apply(calculate_cdf)


def calculate_long_term_monthly_cdf(data_array):
    """Calculate the long-term CDF for each month."""
    return data_array.groupby('time.month').apply(lambda x: calculate_cdf(x.stack(z=('time',))))  # Assuming 'time' is sufficient


# def calculate_finkelstein_schaefer_statistic(cdf_monthly, cdf_long_term):
#     """Compute Finkelstein-Schaefer statistic for each month."""
#     return abs(cdf_monthly - cdf_long_term).sum()


def calculate_finkelstein_schaefer_statistic(cdf_long_term):
    """Wrapper function to compute Finkelstein-Schaefer statistic using map on xarray groupby."""
    def inner_function(cdf_monthly):
        """Compute Finkelstein-Schaefer statistic for each month."""
        return abs(cdf_monthly - cdf_long_term).sum()
    return inner_function


def calculate_weighted_sum(fs_dict, weights):
    """ Calculate weighted sum of FS statistics for each variable. """
    ws = sum(fs_dict[var] * weight for var, weight in weights.items())
    return ws


def calculate_tmy(
    time_series,
    longitude: float,
    latitude: float,
    timestamps: DatetimeIndex = str(now_datetime()),
    start_time: Optional[datetime] = None,  # Used by a callback function
    periods: Optional[int] = None,  # Used by a callback function
    frequency: Optional[str] = None,  # Used by a callback function
    end_time: Optional[datetime] = None,  # Used by a callback function
    variable: Optional[str] = None,
    variable_name_as_suffix: bool = True,
    neighbor_lookup: MethodForInexactMatches = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the Typical Meteorological Year.

    Calculate the Typical Meteorological Year based on the following algorithm
    :

        1. Read _at least_ 10 years of hourly time series over a location

        2. Compute daily maximum, minimum and mean of selected variables (cf. weight list below).
        
        3. Compute the cumulative distribution function (CDF) of each variable for each month:

            3.1 one cumulative distribution function for each variable, each month and each year of data
                # e.g. for the GHI: one for Jan. 2011, one for Jan. 2012, one for Jan 2013, ... and for each month
                # the same for TAmb, or other variables
            
            3.2 one long-term cumulative distribution function for each variable and each month 
                # e.g. one for GHI for January containing all daily values for 2011 to 2020
        
        4. Compute the weighted sum (WS) of the Finkelstein-Schafer statistic (FS) for each variable:
            
            4.1 Compute FS, the sum over n days of a month the absolute difference between the long-term CDF and the candidate month CDF at value xi
            
            4.2 Compute WS, the weighted sum of FS for each month of each year
        
        5. Rank each months by lowest weighted sum WS (rank every January, every February, ...)
        
        6. Select each month based on various criteria defined in the different norms/methods
            - The final step for choosing months in the ISO norm is to compare the wind speed of the best 3 months from the ranked WS to the long-term average and choose the one with the lowest difference.
            - For the Sandia and NREL methods, the best 5 months from the ranked WS are re-ranked by their closeness to the long-term average and median. The 5 months are then filtered by analyzing the frequency and length of extrema in ambient temperature and global horizontal irradiance.
        
        7. Concatenate the selected months into a single continuous year (e.g. Jan 2015, Feb 2011, Mar 2017, etc...), interpolate the values of different variables at the month boundaries to smooth out discontinuities. 
    """
    # 1. Read _at least_ 10 years of hourly time series over a location
    location_series_data_array = select_time_series(
        time_series=time_series,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        start_time=start_time,
        end_time=end_time,
        # convert_longitude_360=convert_longitude_360,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        variable_name_as_suffix=variable_name_as_suffix,
        verbose=verbose,
    )
    logger.debug(f'Selected time series data array: {location_series_data_array}')

    # # 2
    # daily_univariate_statistics = calculate_daily_univariate_statistics(
    #     data_array=location_series_data_array
    # )
    
    # # 3. using mean daily values for simplicity ?
    # monthly_cdfs = calculate_monthly_cdfs(daily_univariate_statistics['mean'])
    # print(f'{monthly_cdfs=}')
    # long_term_cdf = calculate_long_term_monthly_cdf(daily_univariate_statistics['mean'])
   
    # # 4. weighted sum of Finkelstein-Schafer statistic for each month-year
    # fs_statistic = calculate_finkelstein_schaefer_statistic(
    #         cdf_long_term=long_term_cdf,
    #         cdf_monthly=monthly_cdfs,
    #         )
    # fs_scores = monthly_cdfs.groupby("month", squeeze=False).map(
    #     calculate_finkelstein_schaefer_statistic, cdf_long_term=long_term_cdf
    # )
    # weights = xr.DataArray([1.23]*12, dims=["month"], coords={"month": range(1, 13)})
    # weighted_fs_scores = (fs_scores * weights).groupby('month', squeeze=False).sum()
    
    # # 5/6. Select months with lowest FS across all years
    # typical_months = weighted_fs_scores.argmin(dim='month')

    # # 7. Concatenate typical months into one continuous year (TMY)
    # tmy_data = [daily_univariate_statistics.sel(time=typical_months.sel(month=month)) for month in range(1, 13)]

    daily_univariate_statistics = calculate_daily_univariate_statistics(location_series_data_array)
    logger.debug(f'Daily univariate statistics: {daily_univariate_statistics}')
    print(f'Daily univariate statistics: {daily_univariate_statistics}')

    monthly_cdfs = calculate_monthly_cdfs(daily_univariate_statistics['mean'])
    logger.debug(f'Monthly CDFs: {monthly_cdfs}')
    print(f'Monthly CDFs: {monthly_cdfs}')

    long_term_cdf = calculate_long_term_monthly_cdf(daily_univariate_statistics['mean'])
    logger.debug(f'Long term monthly CDF: {long_term_cdf}')
    print(f'Long term monthly CDF: {long_term_cdf}')

    # generate a function for `map()`
    fs_function = calculate_finkelstein_schaefer_statistic(long_term_cdf)
    # apply fs_function on monthly CDFs, grouped by month
    fs_scores = monthly_cdfs.groupby('month', squeeze=False).map(fs_function)
    logger.debug(f'FS scores: {fs_scores}')
    print(f'FS scores: {fs_scores}')

    fs_weights = xr.DataArray([1.23]*12, dims=["month"], coords={"month": range(1, 13)})
    logger.debug(f'FS weights: {fs_weights}')
    print(f'FS weights: {fs_weights}')
    
    weighted_fs_scores = (fs_scores * fs_weights).groupby('month', squeeze=False).sum()
    logger.debug(f'Weighted FS scores: {weighted_fs_scores}')
    print(f'Weighted FS scores: {weighted_fs_scores}')

    typical_months = weighted_fs_scores.argmin(dim='month')
    # Hypothetical computation of typical_months, ensuring it contains datetime indices
    # typical_months = xr.DataArray(pd.date_range('2005-01-01', periods=12, freq='MS'), dims=['month'])
    logger.debug(f'Typical months: {typical_months}')
    print(f'Typical months: {typical_months}')

    # Assuming typical_months correctly holds datetime indices now
    tmy_data = [daily_univariate_statistics.sel(time=month) for month in typical_months]
    
    tmy_data = [daily_univariate_statistics.sel(time=typical_months.sel(month=month)) for month in range(1, 13)]
    tmy = xr.concat(tmy_data, dim='time')

    return tmy 
