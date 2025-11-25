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
from xarray import DataArray


@log_function_call
def calculate_ecdf(sample):
    """Calculate the empirical cumulative distribution function (CDF) of the data, ensuring unique coordinates."""
    from scipy.stats import ecdf

    ecdfs = ecdf(sample)
    return DataArray(
        ecdfs.cdf.probabilities, coords=[ecdfs.cdf.quantiles], dims=["quantile"]
    )


@log_function_call
def calculate_yearly_monthly_ecdfs(
    dataset,
    variable,
):
    """Calculate monthly CDFs for each variable for each month and year."""
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
    return dataset[variable].groupby("time.month").map(lambda x: calculate_ecdf(x))
