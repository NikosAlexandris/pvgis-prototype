"""
"""

from devtools import debug
from pvgisprototype.algorithms.tmy.models import FinkelsteinSchaferStatisticModel
from pvgisprototype.log import log_function_call
from xarray import merge
from datetime import datetime
from pandas import DatetimeIndex, Timestamp
from typing import Sequence
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL, NOT_AVAILABLE, VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import NEIGHBOR_LOOKUP_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT
from pvgisprototype.algorithms.tmy.weighting_scheme_model import MeteorologicalVariable, TypicalMeteorologicalMonthWeightingScheme
from pvgisprototype.algorithms.tmy.weighting_scheme_model import TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT
from pvgisprototype.algorithms.tmy.finkelstein_schafer import calculate_finkelstein_schafer_statistics

@log_function_call
def calculate_weighted_sum(finkelstein_schafer_statistic, weights):
    """Calculate weighted sum of Finkelstein-Schafer statistics for each variable."""
    return sum(finkelstein_schafer_statistic[var] * weight for var, weight in weights.items())


@log_function_call
def calculate_tmy(
    time_series,
    meteorological_variables: Sequence[MeteorologicalVariable],
    longitude: float = float(),
    latitude: float = float(),
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
    """Calculate the Typical Meteorological Year (TMY)

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
            difference.

            6.2 For the Sandia and NREL methods, the best 5 months
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

    tmy_statistics = {}
    for meteorological_variable in meteorological_variables:

        # 1 Finkelstein-Schafer statistic for each month and year
        finkelstein_schafer_statistics = calculate_finkelstein_schafer_statistics(
            time_series=time_series,
            meteorological_variable=meteorological_variable,
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
        )
        ranked_finkelstein_schafer_statistic = finkelstein_schafer_statistics.get(
            FinkelsteinSchaferStatisticModel.ranked, NOT_AVAILABLE
        )
        # 2 Select the best year for each month (based on FS ranking)
        typical_months = ranked_finkelstein_schafer_statistic.groupby(
            "month", squeeze=False
        ).apply(lambda group: group.argmin(dim="year"))

        # 3 Select time series from which to extract typical months
        location_series = select_time_series(
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
        typical_meteorological_months = []
        for month_index, year_index in enumerate(typical_months):
            year_month = ranked_finkelstein_schafer_statistic.isel(year=year_index, month=month_index)
            month = year_month.month.values
            year = year_month.year.values

            selected_month_data = location_series.sel(
                time=f"{year}-{month:02d}"
            )
            # convert month and year to dimensions -- then, easier to work with !
            selected_month_data = selected_month_data.expand_dims(year=[year], month=[month])
            typical_meteorological_months.append(selected_month_data)

        # 4 Merge selected months
        tmy = merge(typical_meteorological_months)
        # 4 Concatenate selected months
        # tmy = concat(typical_meteorological_months, dim='time')

        # # 5 Smooth discontinuities between months ? ------------------------
        # tmy_smoothed = tmy.interpolate_na(dim="time", method="linear")
        # --------------------------------------------------------------------

        components_container = {
            "Metadata": lambda: {
            },
            "TMY": lambda: {
                "TMY": tmy,
                "Typical months": typical_months,
            },
            "Input data": lambda: {
                meteorological_variable: location_series,
            },
        }
        components = {}
        for _, component in components_container.items():
            components.update(component())

        tmy_statistics[meteorological_variable] = components | finkelstein_schafer_statistics

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return tmy_statistics
