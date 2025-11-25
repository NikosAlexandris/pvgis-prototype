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
    return data_array.expand_dims(year=reference_array.year).broadcast_like(
        reference_array
    )


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
        variable="mean",
    )

    # 3
    long_term_monthly_ecdfs = calculate_long_term_monthly_ecdfs(
        dataset=daily_statistics,
        variable="mean",
    )

    # align to yearly_monthly_ecdfs to enable subtraction
    aligned_long_term_monthly_ecdfs = align_and_broadcast(
        long_term_monthly_ecdfs, yearly_monthly_ecdfs
    )

    # 5
    finkelstein_schafer_statistic = abs(
        yearly_monthly_ecdfs - aligned_long_term_monthly_ecdfs
    ).sum(dim="quantile")

    return (
        finkelstein_schafer_statistic,
        daily_statistics,
        yearly_monthly_ecdfs,
        long_term_monthly_ecdfs,
    )
