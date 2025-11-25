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
from devtools import debug
from xarray import concat
from pvgisprototype.api.tmy.models import FinkelsteinSchaferStatisticModel
from pvgisprototype.api.tmy.typical_month import select_typical_month_iso_15927_4
from pvgisprototype.log import log_function_call
from pandas import DatetimeIndex, Timestamp
from typing import Sequence, Dict
from pvgisprototype.constants import (
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    FINGERPRINT_FLAG_DEFAULT,
    NOT_AVAILABLE,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype import TypicalMeteorologicalVariableYear
from pvgisprototype.api.tmy.weighting_scheme_model import (
    MeteorologicalVariable,
    TypicalMeteorologicalMonthWeightingScheme,
    TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT,
)
from pvgisprototype.api.tmy.finkelstein_schafer import (
    model_weighted_finkelstein_schafer_statistics,
)
from pvgisprototype.log import logger


@log_function_call
def calculate_weighted_sum(finkelstein_schafer_statistic, weights):
    """Calculate weighted sum of Finkelstein-Schafer statistics for each variable."""
    return sum(finkelstein_schafer_statistic[var] * weight for var, weight in weights.items())


@log_function_call
def calculate_tmy(
    # time_series,
    meteorological_variables: Sequence[MeteorologicalVariable],
    temperature_series,  #: numpy.ndarray = numpy.array(TEMPERATURE_DEFAULT),
    relative_humidity_series,
    wind_speed_series,  #: numpy.ndarray = numpy.array(WIND_SPEED_DEFAULT),
    # wind_speed_variable: str | None,
    global_horizontal_irradiance,  #: ndarray | None = None,
    direct_normal_irradiance,  #: ndarray | None = None,
    timestamps: Timestamp | DatetimeIndex = Timestamp.now(),
    weighting_scheme: TypicalMeteorologicalMonthWeightingScheme = TYPICAL_METEOROLOGICAL_MONTH_WEIGHTING_SCHEME_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
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

    .. [3] https://www.sciencedirect.com/science/article/pii/S0960148120311009?via%3Dihub

    """
    # For each meteorological variable of
    # air temperature, relative humidity and solar radiation

    # Map variables to their data series
    variable_series_map: Dict[MeteorologicalVariable, any] = {
        MeteorologicalVariable.MIN_DRY_BULB_TEMPERATURE: temperature_series,
        MeteorologicalVariable.MEAN_DRY_BULB_TEMPERATURE: temperature_series,
        MeteorologicalVariable.MAX_DRY_BULB_TEMPERATURE: temperature_series,
        MeteorologicalVariable.MEAN_RELATIVE_HUMIDITY: relative_humidity_series,
        MeteorologicalVariable.MEAN_WIND_SPEED: wind_speed_series,
        MeteorologicalVariable.GLOBAL_HORIZONTAL_IRRADIANCE: global_horizontal_irradiance,
        MeteorologicalVariable.DIRECT_NORMAL_IRRADIANCE: direct_normal_irradiance,
    }

    # Filter map to only variables requested
    filtered_variable_map = {
        var: data
        for var, data in variable_series_map.items()
        if var in meteorological_variables
    }

    results = {}

    for meteorological_variable, time_series in filtered_variable_map.items():
        logger.info(
            f"Processing series of {meteorological_variable.value}",
            alt=f"Processing series of [code]{meteorological_variable.value}[/code]"
        )
        print(f"{meteorological_variable.value}")

        # 1 Finkelstein-Schafer statistic for each month and year
        finkelstein_schafer_statistics = model_weighted_finkelstein_schafer_statistics(
            time_series=time_series,
            meteorological_variable=meteorological_variable,
            weighting_scheme=weighting_scheme,
            verbose=verbose,
        )
        ranked_finkelstein_schafer_statistic = finkelstein_schafer_statistics.get(
            FinkelsteinSchaferStatisticModel.ranked, NOT_AVAILABLE
        )

        # 2 Select the "typical" year for each month (
        typical_months = select_typical_month_iso_15927_4(
            ranked_fs_statistic=ranked_finkelstein_schafer_statistic,
            wind_speed_series=wind_speed_series,
            # wind_speed_variable=wind_speed_variable,
            timestamps=timestamps,
            verbose=verbose,
        )

        # After collecting selected months, reassemble into continuous TMY
        typical_meteorological_months = []

        for month_num in typical_months.month.values:
            selected_year = int(typical_months.sel(month=month_num).values)
            
            # Extract the month data from its source year
            selected_month_data = time_series.sel(time=f"{selected_year}-{month_num:02d}")
            
            typical_meteorological_months.append(selected_month_data)

        # # 4 Merge selected months
        # tmy = merge(typical_meteorological_months)

        # 4 Concatenate selected months along time dimension
        tmy = concat(typical_meteorological_months, dim='time')

        # Create synthetic timestamps for a continuous typical year
        # Use a reference year (e.g., 2005 or first year in dataset)
        reference_year = int(time_series.time.dt.year.min().values)

        # Generate new timestamps mapping to the reference year
        original_times = tmy.time.values
        new_times = []

        for _index, original_time in enumerate(original_times):
            original_dt = Timestamp(original_time)
            # Map to same month/day/hour in reference year
            new_time = original_dt.replace(year=reference_year)
            new_times.append(new_time)

        # Assign the synthetic timestamps
        tmy = tmy.assign_coords(time=('time', new_times))

        # Add month and year as coordinates for plotting
        tmy = tmy.assign_coords(
            month=('time', tmy.time.dt.month.values),
            year=('time', [reference_year] * len(tmy.time))
        )


        # Step 5: Wrap in data model and build output
        tmy_model = TypicalMeteorologicalVariableYear(
            value=tmy.values if hasattr(tmy, 'values') else tmy,  # Keep this too
            tmy=tmy,
            weighting_scheme=weighting_scheme,
            finkelstein_schafer_statistics=finkelstein_schafer_statistics,
            wind_speed=wind_speed_series,
            meteorological_variable=meteorological_variable.value,
            typical_months=typical_months,
        )
        tmy_model.build_output(
            verbose=verbose,
            fingerprint=fingerprint,
        )

        # # # 5 Smooth discontinuities between months ? ------------------------
        # # tmy_smoothed = tmy.interpolate_na(dim="time", method="linear")
        # # --------------------------------------------------------------------

        results[meteorological_variable] = tmy_model.output

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return results
