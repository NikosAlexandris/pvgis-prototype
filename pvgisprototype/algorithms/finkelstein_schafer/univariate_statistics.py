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


@log_function_call
def calculate_daily_univariate_statistics(
    data_array: DataArray,
) -> Dataset:
    """
    Calculate daily maximum, minimum, and mean for each variable in the dataset using pandas.
    Preserves latitude (lat) and longitude (lon) coordinates of the original data.
    """
    # Convert xarray DataArray to pandas DataFrame and resample to daily frequency and compute statistics
    daily_statistics = (
        data_array.to_dataframe(name="value").resample("1D").agg(["max", "min", "mean"])
    )

    # Extract lat/lon from the original data_array
    lat = data_array.coords["lat"].values if "lat" in data_array.coords else None
    lon = data_array.coords["lon"].values if "lon" in data_array.coords else None

    # Convert pandas DataFrame back to xarray Dataset
    result = Dataset(
        {
            "max": (["time"], daily_statistics["value"]["max"].values),
            "min": (["time"], daily_statistics["value"]["min"].values),
            "mean": (["time"], daily_statistics["value"]["mean"].values),
        },
        coords={
            "lon": lon,
            "lat": lat,
            "time": daily_statistics.index,
        },
    )

    return result
