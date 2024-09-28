"""
"""

from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from pvgisprototype.log import logger
from datetime import datetime
from pvgisprototype.api.datetime.now import now_datetime
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
from pvgisprototype.algorithms.tmy.weighting_scheme_model import TypicalMeteorologicalMonthWeightingScheme
from pvgisprototype.algorithms.tmy.weighting_scheme_model import TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT
from pvgisprototype.algorithms.tmy.weighting_scheme_model import get_typical_meteorological_month_weighting_scheme

from pvgisprototype.algorithms.tmy.plot import plot_yearly_monthly_ecdfs
from pvgisprototype.algorithms.tmy.plot import plot_yearly_monthly_ecdfs_with_seaborn
from pvgisprototype.algorithms.tmy.plot import plot_long_term_monthly_ecdfs
from pvgisprototype.algorithms.tmy.plot import plot_finkelstein_schafer_statistic
from pvgisprototype.algorithms.tmy.plot import plot_ranked_finkelstein_schafer_statistic


@log_function_call
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


@log_function_call
def calculate_ecdf(sample):
    """Calculate the empirical cumulative distribution function (CDF) of the data, ensuring unique coordinates."""
    from scipy.stats import ecdf

    ecdfs = ecdf(sample)
    return xr.DataArray(ecdfs.cdf.probabilities, coords=[ecdfs.cdf.quantiles], dims=["quantile"])


@log_function_call
def calculate_yearly_monthly_ecdfs(
    dataset,
    variable,
):
    """Calculate monthly CDFs for each variable for each month and year."""
    # annual_ecdfs = t2m['era5_t2m'].groupby('time.year').map(lambda x: x.groupby('time.month').map(lambda y: calculate_ecdf(y)))
    return (
        dataset[variable]
        .groupby("time.year")
        .map(lambda x: x.groupby("time.month").map(lambda y: calculate_ecdf(y)))
    )


@log_function_call
def calculate_long_term_monthly_ecdfs(
    dataset,
    variable,
):
    """Calculate the long-term CDF for each month."""
    ##3
    # long_term_ecdf = t2m['era5_t2m'].groupby('time.month').map(lambda x: calculate_ecdf(x))
    # long_term_ecdf_aligned = long_term_ecdf.expand_dims(year=annual_ecdfs.year).broadcast_like(annual_ecdfs)
    return dataset[variable].groupby("time.month").map(lambda x: calculate_ecdf(x))


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
def calculate_finkelstein_schafer_statistic(
    # yearly_monthly_cdfs,
    # long_term_monthly_cdfs,
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
    weighting_scheme: TypicalMeteorologicalMonthWeightingScheme = TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    plot: bool = False,
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
    # 1. Read _at least_ 10 years of hourly time series over a location
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
    if plot:
        plot_yearly_monthly_ecdfs(yearly_monthly_ecdfs)
        # plot_yearly_monthly_ecdfs_with_seaborn(yearly_monthly_ecdfs)

    # 4
    long_term_monthly_ecdfs = calculate_long_term_monthly_ecdfs(
            dataset=daily_statistics,
            variable='mean',
    )
    if plot:  # plot before alignment !
        plot_long_term_monthly_ecdfs(long_term_monthly_ecdfs)

    # align to yearly_monthly_ecdfs to enable subtraction
    long_term_monthly_ecdfs = align_and_broadcast(
        long_term_monthly_ecdfs, yearly_monthly_ecdfs
    )

    # 5
    finkelstein_schafer_statistic = abs(
        yearly_monthly_ecdfs - long_term_monthly_ecdfs
    ).sum(dim="quantile")
    if plot:
        plot_finkelstein_schafer_statistic(finkelstein_schafer_statistic)

    # Weighting as per alternative TMY algorithms
    mean_dry_bulb_temperature = "Mean Dry Bulb Temperature"
    typical_meteorological_month_weights = (
        get_typical_meteorological_month_weighting_scheme(
            weighting_scheme, variable=mean_dry_bulb_temperature
        )
    )
    logger.debug(f'FS weights: {typical_meteorological_month_weights}')
    
    weighted_finkelstein_schafer_statistic = finkelstein_schafer_statistic * typical_meteorological_month_weights
    if plot:
        plot_finkelstein_schafer_statistic(
            weighted_finkelstein_schafer_statistic,
            plot_path="ranked_finkelstein_schafer_statistic.png",
        )

    ranked_finkelstein_schafer_statistic = weighted_finkelstein_schafer_statistic.rank(dim='year', keep_attrs=True)
    # if plot:
    #     plot_ranked_finkelstein_schafer_statistic(ranked_finkelstein_schafer_statistic)

    from devtools import debug
    debug(locals())
    return ranked_finkelstein_schafer_statistic


@log_function_call
def calculate_weighted_sum(finkelstein_schafer_statistic, weights):
    """Calculate weighted sum of Finkelstein-Schafer statistics for each variable."""
    return sum(finkelstein_schafer_statistic[var] * weight for var, weight in weights.items())


@log_function_call
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
    weighting_scheme: TypicalMeteorologicalMonthWeightingScheme = TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    plot: bool = False,
):
    """Calculate the Typical Meteorological Year.

    Calculate the Typical Meteorological Year using the default ISO 15927-4
    standard or other methods.

    Notes
    -----
    ISO 15927-4

    The procedure to construct Typical Meteorological Years (TMY) follows the
    ISO 15927-4 [0]_ standard. For each month in the year, the data are taken
    from the year calculated as most “typical” for that month. The Standard
    specifies the method to construct the TMY based on a statistical evaluation
    of air temperature, relative humidity and solar radiation, with a less
    important contribution from the wind speed data.

        1. For each of the three quantities (air temperature, relative humidity
        and solar radiation), calculate the daily means from the hourly values.

        2. For each quantity q and each month m, calculate the cumulative
        distribution function 𝜙(𝑞,𝑚) using all the daily values for all years.
        
        3. For each quantity q, each year y and each month m, calculate the
        cumulative distribution function 𝐹(𝑞,𝑚,𝑦) using all the daily values
        for that year.
        
        4. For each q, m and y, calculate the Finkelstein–Schafer statistic,
        summing over the range of the distribution values:
        𝐹𝑆(𝑞,𝑚,𝑦) = ∑|𝐹(𝑞,𝑚,𝑦) − 𝜙(𝑞,𝑚,𝑦)|.  Equation (1) in [1]_
        
        5. For each m and q, rank the the individual months in the multi-year
        period in order of increasing 𝐹𝑆(𝑞,𝑚,𝑦).
        
        6. For each m and y, add the ranks for the three quantities.
        
        7. For each m, for the three months with the lowest total ranking,
        calculate the deviation of the monthly average wind speed from the
        multi-year mean for that month. The lowest deviation in wind speed is
        used to select the “best” month to be included in the TMY.


    Common algorithm outlined in PVSyst [2]_

        Calculate the Typical Meteorological Year based on the following
        algorithm:

        1. Read _at least_ 10 years of hourly time series over a location

        2. Compute daily maximum, minimum and mean of selected variables (cf.
        weight list below).
        
        3. Compute the cumulative distribution function (CDF) of each variable
        for each month:

            3.1 one cumulative distribution function for each variable, each
            month and each year of data e.g. for the GHI: one for Jan. 2011,
            one for Jan. 2012, one for Jan 2013, ... and for each month the
            same for TAmb, or other variables
            
            3.2 one long-term cumulative distribution function for each
            variable and each month e.g. one for GHI for January containing all
            daily values for 2011 to 2020
        
        4. Compute the weighted sum (WS) of the Finkelstein-Schafer statistic
        (FS) for each variable:
            
            4.1 Compute FS, the sum over n days of a month the absolute
            difference between the long-term CDF and the candidate month CDF at
            value xi
            
            4.2 Compute WS, the weighted sum of FS for each month of each year
        
        5. Rank each months by lowest weighted sum WS (rank every January,
        every February, ...)
        
        6. Select each month based on various criteria defined in the different
        norms/methods

            6.1 The final step for choosing months in the ISO norm is to
            compare the wind speed of the best 3 months from the ranked WS to
            the long-term average and choose the one with the lowest
            difference. 6.2 For the Sandia and NREL methods, the best 5 months
            from the ranked WS are re-ranked by their closeness to the
            long-term average and median. The 5 months are then filtered by
            analyzing the frequency and length of extrema in ambient
            temperature and global horizontal irradiance.
        
        7. Concatenate the selected months into a single continuous year (e.g.
        Jan 2015, Feb 2011, Mar 2017, etc...), interpolate the values of
        different variables at the month boundaries to smooth out
        discontinuities. 

    References
    ----------
    .. [0] International Organization for Standardization (ISO). ISO 15927-4.
    Hygrothermal Performance of Buildings—Calculation and Presentation of
    Climatic Data—Part 4: Hourly Data for Assessing the Annual Energy Use for
    Heating and Cooling; Technical Report; Iternational Organization for
    Standardization: Geneva, Switzerland, 2005.

    .. [1] https://doi.org/10.3390/atmos9020053 

    .. [2] https://www.pvsyst.com/help/meteo_tmy_algorithms.htm

    """
    # For each meteorological variable of
    # air temperature, relative humidity and solar radiation

    # for variable in time_series:
    ranked_finkelstein_schafer_statistic = calculate_finkelstein_schafer_statistic(
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
        weighting_scheme=weighting_scheme,
        variable_name_as_suffix=variable_name_as_suffix,
        verbose=verbose,
        plot=plot,
    )

    # tmy_data = [daily_statistics.sel(time=month) for month in typical_months]
    # tmy_data = [daily_statistics.sel(time=typical_months.sel(month=month)) for month in range(1, 13)]
    # tmy = xr.concat(tmy_data, dim='time')

    # return tmy 
    return ranked_finkelstein_schafer_statistic
