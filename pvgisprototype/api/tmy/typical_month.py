# Copyright (C) 2025 European Union
#
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# * https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
# * Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an "AS IS" basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.

from pvgisprototype.log import log_function_call
import xarray as xr
import numpy as np


@log_function_call
def select_typical_month_iso_15927_4(
    ranked_fs_statistic,
    wind_speed_series,
    # wind_speed_variable=None,
    timestamps=None,  # Need this to index by time
    verbose=0,
):
    """Select a typical meteorological month for each calendar month using ISO
    15927-4 method.
    
    ISO 15927-4 specifies that for each calendar month, if using the three
    top-ranked months (lowest FS statistic), the final selection should be
    based on wind speed deviation from the multi-year mean.
    
    Parameters
    ----------
    ranked_fs_statistic : xarray.DataArray
        Ranked Finkelstein-Schafer statistics with dimensions (month, year)
    wind_speed_series : xarray.Dataset
        Time series data containing wind speed and other variables
    wind_speed_variable : str
        Name of the wind speed variable in the dataset
    verbose : int
        Verbosity level for debugging
        
    Returns
    -------
    typical_months : dict
        Dictionary mapping calendar month (1-12) to (year, wind_speed_deviation)


    Notes
    -----

    ISO 15927-4 Step 7 implementation.
    
    For each calendar month:

    1. Get the 3 candidate months (from different years) with lowest FS ranking
    2. Calculate wind speed deviation from long-term mean for each candidate
    3. Select the candidate with smallest wind speed deviation

    """
    typical_months = {}

    # Extract wind speed values (assuming WindSpeedSeries has .value attribute)
    # Adjust this based on your actual WindSpeedSeries structure
    wind_speed = (
        wind_speed_series.value
        if hasattr(wind_speed_series, "value")
        else wind_speed_series
    )

    # For each calendar month (1-12)
    for month in range(1, 13):
        # if verbose > 1:
        #     print(f"\nProcessing month {month}")

        # Step 7a: Get the 3 months with lowest FS ranking for this calendar month
        # ranked_fs_statistic has dims (year, month)
        month_fs_scores = ranked_fs_statistic.sel(month=month)  # Shape: (n_years,)

        # Sort from lowest to highest
        sorted_indices = np.argsort(month_fs_scores.values)

        # Get indices of 3 lowest FS scores (best candidates)
        lowest_3_fs_scores = sorted_indices[:3]

        # Get the actual years corresponding to these 3 candidates
        candidate_years = ranked_fs_statistic.year.values[lowest_3_fs_scores]

        if verbose > 2:
            print(f"  Candidate years : {candidate_years}")
            print(f"  Scores : {month_fs_scores.values[lowest_3_fs_scores]}")

        # Step 7b: Calculate long-term mean wind speed for this calendar month
        # (averaging across all years)
        mask_all_years_this_month = timestamps.month == month
        long_term_wind_speed_mean = wind_speed[mask_all_years_this_month].mean()

        if verbose > 2:
            print(
                f"  Long-term wind speed mean for month {month}: {long_term_wind_speed_mean:.3f}"
            )

        # Step 7c: For each of the 3 candidates, calculate deviation from long-term mean
        wind_speed_deviations = []
        for year in candidate_years:
            # Select wind data for this specific year-month combination
            mask = (timestamps.year == year) & (timestamps.month == month)
            this_year_month_wind_speed = wind_speed[mask]

            # Calculate mean wind speed for this candidate month
            this_year_month_wind_speed_mean = this_year_month_wind_speed.mean()

            # Calculate absolute deviation from long-term mean
            wind_speed_deviation = abs(
                this_year_month_wind_speed_mean - long_term_wind_speed_mean
            )
            wind_speed_deviations.append(wind_speed_deviation)

            if verbose > 2:
                print(
                    f"    Year {year} : mean = {this_year_month_wind_speed_mean :.3f}, deviation = {wind_speed_deviation:.3f}"
                )

        # Step 7d: Select the year with the LOWEST wind speed deviation == typical conditions
        lowest_wind_speed_deviation_idx = np.argmin(wind_speed_deviations)
        selected_year = candidate_years[lowest_wind_speed_deviation_idx]
        typical_months[month] = int(selected_year)

        if verbose > 1:
            print(
                f"- Month/Year  {month}/{selected_year} "
                f"  (Deviation: {wind_speed_deviations[lowest_wind_speed_deviation_idx]:.3f})"
            )

    # Package as Xarray
    typical_months = xr.DataArray(
        data=list(typical_months.values()),
        dims=["month"],
        coords={"month": list(typical_months.keys())},
    )

    return typical_months
