from pvgisprototype.log import log_function_call
from xarray import DataArray
import numpy as np


@log_function_call
def calculate_ecdf(sample):
    """Calculate the empirical cumulative distribution function (CDF) using numpy."""
    sample_sorted = np.sort(sample)
    probabilities = np.arange(1, len(sample_sorted) + 1) / len(sample_sorted)
    return sample_sorted, probabilities

@log_function_call
def calculate_yearly_monthly_ecdfs(dataset, variable):
    """Calculate monthly ECDFs for each variable for each month and year."""
    # Convert the xarray DataArray to pandas DataFrame
    df = dataset[variable].to_dataframe().reset_index()

    # Extract year and month for grouping
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month

    # Pre-calculate global quantiles to ensure alignment
    global_quantiles = np.sort(df[variable].unique())

    # Extract unique years and months
    unique_years = np.sort(df["year"].unique())
    unique_months = np.sort(df["month"].unique())

    # Preallocate the 3D result array
    result_array = np.full((len(unique_years), len(unique_months), len(global_quantiles)), np.nan)

    # Group by year and month and process in one loop
    grouped = df.groupby(["year", "month"])
    for (year, month), group in grouped:
        year_idx = np.searchsorted(unique_years, year)
        month_idx = np.searchsorted(unique_months, month)

        # Calculate ECDF for the group
        sorted_sample, probabilities = calculate_ecdf(group[variable].values)

        # Interpolate probabilities to match global quantiles
        interp_probabilities = np.interp(global_quantiles, sorted_sample, probabilities, left=0, right=1)

        # Store the interpolated probabilities in the result array
        result_array[year_idx, month_idx, :] = interp_probabilities

    # Convert back to an xarray DataArray
    result = DataArray(
        data=result_array,
        dims=["year", "month", "quantile"],
        coords={
            "year": unique_years,
            "month": unique_months,
            "quantile": global_quantiles,
        },
    )
    return result

@log_function_call
def calculate_long_term_monthly_ecdfs(dataset, variable):
    """Calculate the long-term CDF for each month."""
    # Convert the xarray DataArray to pandas DataFrame
    df = dataset[variable].to_dataframe().reset_index()

    # Extract the month for grouping
    df["month"] = df["time"].dt.month

    # Pre-calculate global quantiles to ensure alignment
    global_quantiles = np.sort(df[variable].unique())

    # Extract unique months
    unique_months = np.sort(df["month"].unique())

    # Preallocate the 2D result array
    result_array = np.full((len(unique_months), len(global_quantiles)), np.nan)

    # Group by month and process
    grouped = df.groupby("month")
    for month, group in grouped:
        month_idx = np.searchsorted(unique_months, month)

        # Calculate ECDF for the group
        sorted_sample, probabilities = calculate_ecdf(group[variable].values)

        # Interpolate probabilities to match global quantiles
        interp_probabilities = np.interp(global_quantiles, sorted_sample, probabilities, left=0, right=1)

        # Store the interpolated probabilities in the result array
        result_array[month_idx, :] = interp_probabilities

    # Convert back to an xarray DataArray
    result = DataArray(
        data=result_array,
        dims=["month", "quantile"],
        coords={
            "month": unique_months,
            "quantile": global_quantiles,
        },
    )
    return result
