"""
Statistics

Wanted results for example for a grid-connected photovoltaic system :

- the average monthly energy production
- the average annual production
- year-to-year variability : the standard deviation of the annual values
  calculated over the period covered by the selected solar radiation database

- Annual Production in kW considering geographic and climatic parameters :
  Yearly PV energy production (kWh):        example: 1066.36

- Annual Irradiation, the potential production of kWhs per m2 :
  Yearly in-plane irradiation (kWh/m2):     example: 1341.06

- Annual Variability in kWh, representing the possible variation between two years :
  Yearly-to-year variability (kWh):         example: 43.48

- Total estimates of losses, considering losses due to the angle, spectral
  effects, and ambient temperature:

  Changes in output due to:

  - Angle of incidence (%):                     example: -3.41
  - Spectral effects (%):                       example: 1.56
  - Temperature and low irradiance (%):         example: -5.75

Total loss (%): 	     -20.48
"""

from typing import Dict, List

import numpy

# from pvgisprototype.constants import DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
# from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME
# from pvgisprototype.constants import REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME
# from pvgisprototype.constants import TEMPERATURE_COLUMN_NAME
# from pvgisprototype.constants import WIND_SPEED_COLUMN_NAME
# from pvgisprototype.constants import SURFACE_TILT_COLUMN_NAME
# from pvgisprototype.constants import SURFACE_ORIENTATION_COLUMN_NAME
import pandas
from xarray import DataArray
from pandas import DatetimeIndex
from scipy.stats import mode

from pvgisprototype.api.utilities.conversions import round_float_values

# from pvgisprototype.constants import EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME
# from pvgisprototype.constants import EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME
# from pvgisprototype.constants import EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME
# from pvgisprototype.constants import EFFICIENCY_COLUMN_NAME
# from pvgisprototype.constants import ALGORITHM_COLUMN_NAME
# from pvgisprototype.constants import TITLE_KEY_NAME
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    SPECTRAL_FACTOR_COLUMN_NAME,
    VERBOSE_LEVEL_DEFAULT,
)

TIME_GROUPINGS = {
    "Y": ("year", "Yearly means"),
    "S": ("season", "Seasonal means"),
    "M": ("month", "Monthly means"),
    "W": ("1W", "Weekly means"),
    "D": ("1D", "Daily means"),
    "H": ("1H", "Hourly means"),
}


def calculate_sum_and_percentage(
    series,
    reference_series,
    rounding_places=None,
    dtype=DATA_TYPE_DEFAULT,
    array_backend=ARRAY_BACKEND_DEFAULT,
):
    """Calculate sum of a series and its percentage relative to a reference series.

    Notes
    -----

    Uses .item() to convert NumPy numerics to standard Python types.
    """
    total = numpy.nansum(series).item()
    if isinstance(total, numpy.ndarray):
        total = total.astype(dtype).item()

    percentage = (total / reference_series * 100) if reference_series != 0 else 0

    if isinstance(percentage, numpy.ndarray):
        percentage.astype(dtype)

    if rounding_places is not None:
        total = round_float_values(total, rounding_places)
        percentage = round_float_values(percentage, rounding_places)

    return total, percentage


def calculate_statistics(
    series,
    timestamps,
    frequency,
    reference_series,
    rounding_places=None,
    dtype=DATA_TYPE_DEFAULT,
    array_backend=ARRAY_BACKEND_DEFAULT,
):
    """Calculate the sum, mean, standard deviation of a series based on a
    specified frequency and its percentage relative to a reference series.
    """
    if frequency == "Single":
        total = series.item()  # total is the single value in the series
        mean = total  # For a single value, the mean is the value itself
        std_dev = 0  # Standard deviation is 0 for a single value
        percentage = (total / reference_series * 100) if reference_series != 0 else 0

        if rounding_places is not None:
            total = round_float_values(total, rounding_places)
            percentage = round_float_values(percentage, rounding_places)

        return total, mean, std_dev, percentage

    pandas_series = pandas.Series(series, timestamps)
    resampled = pandas_series.resample(frequency)
    total = resampled.sum().sum().item()  # convert to Python float
    # if isinstance(total, numpy.ndarray):
    #     total = total.astype(dtype)
    percentage = (total / reference_series * 100) if reference_series != 0 else 0
    # if isinstance(percentage, numpy.ndarray):
    #     percentage.astype(dtype)
    if rounding_places is not None:
        total = round_float_values(total, rounding_places)
        percentage = round_float_values(percentage, rounding_places)
    mean = resampled.mean().mean().item()  # convert to Python float
    std_dev = resampled.std().mean()  # Mean of standard deviations over the period

    return total, mean, std_dev, percentage


def calculate_mean_of_series_per_time_unit(
    series: numpy.ndarray,
    timestamps: DatetimeIndex,
    frequency: str,
):
    """ """
    from devtools import debug

    debug(locals())
    if frequency == "Single" or len(timestamps) == 1:
        return series.mean().item()  # Direct mean for a single value

    pandas_series = pandas.Series(series, index=timestamps)
    print(pandas_series)
    mean = pandas_series.resample(frequency).sum().mean().item()  # convert to float

    print(mean)
    return mean


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
