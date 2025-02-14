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
