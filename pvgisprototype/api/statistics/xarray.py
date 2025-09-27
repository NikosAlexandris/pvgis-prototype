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
from typing import Dict, List
from pandas import DatetimeIndex
from xarray import DataArray
from scipy.stats import mode
import numpy
from pvgisprototype.constants import (
    GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    SPECTRAL_FACTOR_COLUMN_NAME,
)


TIME_GROUPINGS = {
    "Y": ("year", "Yearly means"),
    "S": ("season", "Seasonal means"),
    "M": ("month", "Monthly means"),
    "W": ("1W", "Weekly means"),
    "D": ("1D", "Daily means"),
    "H": ("1H", "Hourly means"),
}


def generate_series_statistics(
    data_xarray: DataArray,
    groupby: str | None = None,
) -> dict:
    """ """
    statistics_container = {
        "Basic": lambda: {
            "Start": data_xarray.time.values[0],
            "End": data_xarray.time.values[-1],
            "Count": data_xarray.count().item(),
            "Min": data_xarray.min().item(),
            "Mean": data_xarray.mean().item(),
            "Max": data_xarray.max().item(),
            "Sum": data_xarray.sum().item(),
        },
        "Extended": lambda: {
            "25th Percentile": numpy.percentile(data_xarray, 25),
            "Median": data_xarray.median().item(),
            "Mode": mode(data_xarray.values.flatten())[0],
            "Variance": data_xarray.var().item(),
            "Standard deviation": data_xarray.std().item(),
        },  # if verbose > 1 else {},
        "Timestamps": lambda: {
            "Time of Min": data_xarray.idxmin("time").values,
            "Index of Min": data_xarray.argmin().item(),
            "Time of Max": data_xarray.idxmax("time").values,
            "Index of Max": data_xarray.argmax().item(),
        },  # if verbose > 2 else {},
        "Coordinates": lambda: (
            {
                "Longitude of Max": data_xarray.argmax("lon").item(),
                "Latitude of Max": data_xarray.argmax("lat").item(),
            }
            if "longitude" in data_xarray.dims and "latitude" in data_xarray.dims
            else {}
        ),
    }
    statistics = {}
    for _, func in statistics_container.items():
        statistics.update(func())

    return statistics


def group_series_statistics(
    data_xarray: DataArray | None,
    irradiance_xarray: DataArray | None,
    statistics: dict,
    groupby: str | None = None,
):
    """ """
    if groupby in TIME_GROUPINGS:
        freq, label = TIME_GROUPINGS[groupby]
        if groupby in ["Y", "M", "S"]:
            statistics[label] = data_xarray.groupby(f"time.{freq}").mean().values
            if irradiance_xarray is not None:
                statistics[GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME] = (
                    irradiance_xarray.groupby(f"time.{freq}").mean().values
                )
        else:
            statistics[label] = data_xarray.resample(time=freq).mean().values
        statistics["Sum of Group Means"] = statistics[label].sum()
        if irradiance_xarray is not None:
            statistics[f"Sum of {GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME}"] = statistics[
                GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME
            ].sum()

    elif groupby:  # custom frequencies like '3H', '2W', etc.
        custom_label = f"{groupby} means"
        statistics[custom_label] = data_xarray.resample(time=groupby).mean().values
        statistics["Sum of Group Means"] = (
            data_xarray.resample(time=groupby).mean().sum().values
        )

    return statistics


def calculate_series_statistics(
    data_array: numpy.ndarray | Dict[str, numpy.ndarray],
    timestamps: DatetimeIndex,
    groupby: str | None = None,
) -> dict:
    """ """
    irradiance_xarray = None  # Ugly Hack :-/
    if isinstance(data_array, dict):
        # First, irradiance may exist only in a dictionary !
        irradiance_xarray = data_array.get(GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME, None)
        if irradiance_xarray is not None:
            irradiance_xarray = DataArray(
                irradiance_xarray,
                coords=[("time", timestamps)],
                name="Effective irradiance series",
            )
            irradiance_xarray.attrs["units"] = "W/m^2"
            irradiance_xarray.attrs["long_name"] = "Effective Solar Irradiance"
            irradiance_xarray.load()

        # Then, the primary wanted data
        data_array = data_array[PHOTOVOLTAIC_POWER_COLUMN_NAME]

    # Regardless of whether the input data_array is an array or a dict :
    data_xarray = DataArray(
        data_array, coords=[("time", timestamps)], name="Effective irradiance series"
    )
    data_xarray.attrs["units"] = "W/m^2"
    data_xarray.attrs["long_name"] = "Photovoltaic power"
    data_xarray.load()
    statistics = generate_series_statistics(data_xarray=data_xarray, groupby=groupby)
    statistics = group_series_statistics(
        data_xarray=data_xarray,
        irradiance_xarray=irradiance_xarray,
        statistics=statistics,
        groupby=groupby,
    )

    return statistics


def calculate_spectral_factor_statistics(
    spectral_factor: Dict,
    spectral_factor_model: List,
    photovoltaic_module_type: List,
    timestamps: DatetimeIndex,
    rounding_places: int | None = 3,
    groupby: str | None = None,
) -> dict:
    """
    Calculate statistics for the spectral factor data.

    Parameters
    ----------
    spectral_factor : Dict
        Dictionary containing spectral factor data.
    spectral_factor_model : List
        List of spectral factor models.
    photovoltaic_module_type : List
        List of photovoltaic module types.
    timestamps : DatetimeIndex
        Timestamps for the data series.
    rounding_places : int
        Decimal places for rounding.
    groupby : str
        Time grouping for statistics, e.g., 'Y', 'M', 'D', etc.

    Returns
    -------
    statistics : dict
        Dictionary with calculated statistics for each model and module type.
    """
    statistics = {}

    for model in spectral_factor_model:
        statistics[model.value] = {}

        for module_type in photovoltaic_module_type:
            # Extract spectral factor data for the model and module type
            spectral_factor_data = (
                spectral_factor.get(model)
                .get(module_type)
                .get(SPECTRAL_FACTOR_COLUMN_NAME)
            )

            if spectral_factor_data is not None:
                # Create an Xarray DataArray for the spectral factor data
                spectral_factor_xarray = DataArray(
                    spectral_factor_data,
                    coords=[("time", timestamps)],
                    name=f"{module_type.value} Spectral Mismatch",
                )
                spectral_factor_xarray.attrs["units"] = "W/m^2"
                spectral_factor_xarray.attrs["long_name"] = (
                    f"{module_type.value} Spectral Factor"
                )

                # Generate basic and extended statistics
                module_statistics = generate_series_statistics(
                    data_xarray=spectral_factor_xarray,
                    groupby=groupby,
                )

                # Add time-grouped statistics (e.g., yearly, monthly) if requested
                module_statistics = group_series_statistics(
                    data_xarray=spectral_factor_xarray,
                    irradiance_xarray=None,
                    statistics=module_statistics,
                    groupby=groupby,
                )

                # Store the statistics for this combination of model and module type
                statistics[model.value][module_type.value] = module_statistics

    return statistics
