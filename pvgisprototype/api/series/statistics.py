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

from devtools import debug
from rich.console import Console
from typing import Union, Dict
import numpy
import xarray as xr
from scipy.stats import mode
from rich.table import Table
from rich.box import SIMPLE, SIMPLE_HEAD, SIMPLE_HEAVY, ROUNDED, HORIZONTALS
import csv
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT, DATA_TYPE_DEFAULT, ROUNDING_PLACES_DEFAULT
from pandas import DatetimeIndex
# from pvgisprototype.constants import TITLE_KEY_NAME
from pvgisprototype.constants import PHOTOVOLTAIC_POWER_COLUMN_NAME
# from pvgisprototype.constants import EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME
# from pvgisprototype.constants import EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME
# from pvgisprototype.constants import EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME
# from pvgisprototype.constants import EFFICIENCY_COLUMN_NAME
# from pvgisprototype.constants import ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME
# from pvgisprototype.constants import DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
# from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME
# from pvgisprototype.constants import REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME
# from pvgisprototype.constants import TEMPERATURE_COLUMN_NAME
# from pvgisprototype.constants import WIND_SPEED_COLUMN_NAME
# from pvgisprototype.constants import SURFACE_TILT_COLUMN_NAME
# from pvgisprototype.constants import SURFACE_ORIENTATION_COLUMN_NAME
import pandas
from pvgisprototype.api.utilities.conversions import round_float_values


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

    percentage = (total / reference_series * 100).item() if reference_series != 0 else 0
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
    """
    """
    pandas_series = pandas.Series(series, index=timestamps)
    return pandas_series.resample(frequency).sum().mean().item()  # convert to float



def calculate_series_statistics(
    data_array: Union[numpy.ndarray, Dict[str, numpy.ndarray]],
    timestamps: DatetimeIndex,
    groupby: str | None = None,
) -> dict:
    """ """
    irradiance_xarray = None  # Ugly Hack :-/
    if isinstance(data_array, dict):

        # First, irradiance may exist only in a dictionary !
        irradiance_xarray = data_array.get(GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME, None)
        if irradiance_xarray is not None:
            irradiance_xarray = xr.DataArray(
                irradiance_xarray,
                coords=[('time', timestamps)],
                name='Effective irradiance series'
            )
            irradiance_xarray.attrs['units'] = 'W/m^2'
            irradiance_xarray.attrs['long_name'] = 'Effective Solar Irradiance'
            irradiance_xarray.load()

        # Then, the primary wanted data
        data_array = data_array[PHOTOVOLTAIC_POWER_COLUMN_NAME]

    # Regardless of whether the input data_array is an array or a dict :
    data_xarray = xr.DataArray(
        data_array,
        coords=[('time', timestamps)],
        name='Effective irradiance series'
    )
    data_xarray.attrs['units'] = 'W/m^2'
    data_xarray.attrs['long_name'] = 'Photovoltaic power'
    data_xarray.load()
    statistics_container = {
        'basic': lambda: {
            'Start': data_xarray.time.values[0],
            'End': data_xarray.time.values[-1],
            'Count': data_xarray.count().values,
            'Min': data_xarray.min().values,
            'Mean': data_xarray.mean().values,
            'Max': data_xarray.max().values,
            'Sum': data_xarray.sum().values,
        },
        'extended': lambda: {
            '25th Percentile': numpy.percentile(data_xarray, 25),
            'Median': data_xarray.median().values,
            'Mode': mode(data_xarray.values.flatten())[0],
            'Variance': data_xarray.var().values,
            'Standard deviation': data_xarray.std().values,
        },# if verbose > 1 else {},
        'timestamps': lambda: {
            'Time of Min': data_xarray.idxmin('time').values,
            'Index of Min': data_xarray.argmin().values,
            'Time of Max': data_xarray.idxmax('time').values,
            'Index of Max': data_xarray.argmax().values,
        },# if verbose > 2 else {},
        'groupby_summary': lambda: {
            'Sum of Group Means': None } if groupby else {},
        # 'Longitude of Max': data_xarray.argmax('lon').values,
        # 'Latitude of Max': data_xarray.argmax('lat').values,
    }
    statistics = {}
    for key, func in statistics_container.items():
        statistics.update(func())

    time_groupings = {
        'Y': ('year', 'Yearly means'),
        'S': ('season', 'Seasonal means'),
        'M': ('month', 'Monthly means'),
        'W': ('1W', 'Weekly means'),
        'D': ('1D', 'Daily means'),
        'H': ('1H', 'Hourly means'),
    }
    if groupby in time_groupings:
        freq, label = time_groupings[groupby]
        if groupby in ['Y', 'M', 'S']:
            statistics[label] = data_xarray.groupby(f'time.{freq}').mean().values
            if irradiance_xarray is not None:
                statistics[GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME] = irradiance_xarray.groupby(f'time.{freq}').mean().values
        else:
            statistics[label] = data_xarray.resample(time=freq).mean().values
        statistics['Sum of Group Means'] = statistics[label].sum()
        if irradiance_xarray is not None:
            statistics[f'Sum of {GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME}'] = statistics[GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME].sum()

    elif groupby:  # custom frequencies like '3H', '2W', etc.
        custom_label = f'{groupby} means'
        statistics[custom_label] = data_xarray.resample(time=groupby).mean().values
        statistics['Sum of Group Means'] = data_xarray.resample(time=groupby).mean().sum().values

    return statistics


def print_series_statistics(
    data_array: numpy.array,
    timestamps: DatetimeIndex,
    title: str ='Time series',
    groupby: str = None,
    monthly_overview: bool = False,
    rounding_places: int = None,
    verbose=0,
) -> None:
    """
    """
    rename_monthly_output_rows = {
        "Sum of Group Means": "Yearly PV energy",
        f"Sum of {GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME}": 'Yearly in-plane irradiance',
    }
    if groupby and groupby.lower() == 'monthly':
        monthly_overview = True

    table = Table(
        title=title,
        caption='Caption text',
        show_header=True,
        header_style="bold magenta",
        row_styles=['none', 'dim'],
        box=SIMPLE_HEAD,
        highlight=True,
    )
    if monthly_overview:  # typical overview !
        table.add_column("Statistic", justify="right", style="bright_blue", no_wrap=True)
        table.add_column("Value", style="cyan")
        # get monthly mean values
        statistics = calculate_series_statistics(data_array, timestamps, 'M')
    else:
        table.add_column("Statistic", justify="right", style="magenta", no_wrap=True)
        table.add_column("Value", style="cyan")
        statistics = calculate_series_statistics(data_array, timestamps, groupby)

    # Basic metadata
    basic_metadata = (
        ["Start", "End", "Count"] if not monthly_overview else ["Start", "End"]
    )
    
    for key in basic_metadata:
        if key in statistics:
            table.add_row(key, str(statistics[key]))

    # grouping_labels = {
    #     'Y': 'Yearly means',
    #     'S': 'Seasonal means',
    #     'M': 'Monthly means',
    #     'W': 'Weekly means',
    #     'D': 'Daily means',
    #     'H': 'Hourly means',
    # }

    # Separate!
    table.add_row("", "")

    # Groups by
    time_groupings = [
        'Yearly means',
        'Seasonal means',
        'Monthly means',
        'Weekly means',
        'Daily means',
        'Hourly means',
        groupby + ' means' if groupby else None,  # do not print custom frequency means
        ]

    if monthly_overview:
        monthly_metadata = [
                # 'Min',
                # 'Mean',
                # 'Max',
                # 'Standard deviation',
                'Sum of Group Means',
                'Irradiance',
               f"Sum of {GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME}",
            ]

    # Index of items
    index_metadata = (
        ["Time of Min", "Index of Min", "Time of Max", "Index of Max"]
        if not monthly_overview
        else []  # 'Time of Min', 'Time of Max',
    )

    # Add statistics
    for key, value in statistics.items():
        if not monthly_overview:
            if key not in basic_metadata and key not in time_groupings and key not in index_metadata:
                # table.add_row(key, str(round_float_values(value, rounding_places)))
                table.add_row(key, str(value))
        else:
            if key in monthly_metadata and key not in basic_metadata and key not in index_metadata:
                # table.add_row(key, str(round_float_values(value, rounding_places)))
                # table.add_row(key, str(value))
                display_key = rename_monthly_output_rows.get(key, key)
                table.add_row(display_key, str(value))

    # Separate!
    table.add_row("", "")

    if monthly_overview:
        key = 'Monthly means'

    # Groups
    custom_freq_label = f'{groupby} means' if groupby and groupby not in time_groupings else None
    for key, value in statistics.items():
        if key in time_groupings:

            if key == 'Yearly means':
                for year, value in enumerate(statistics[key]):
                    table.add_row(str(year), str(value))
                table.add_row("", "")

            elif key == 'Monthly means':
                import calendar
                for idx, value in enumerate(statistics[key], start=1):
                    month_name = calendar.month_name[idx]
                    table.add_row(month_name, str(value))
                table.add_row("", "")

            elif key == 'Seasonal means':
                seasons = ['DJF', 'MAM', 'JJA', 'SON']
                for season, value in zip(seasons, statistics[key]):
                    table.add_row(season, str(value))
                table.add_row("", "")

            elif key == 'Weekly means':
                for idx, value in enumerate(statistics[key]):
                    week_number = idx + 1  # Week number
                    table.add_row(f"Week {week_number}", str(value))
                table.add_row("", "")

            elif key == 'Daily means':  # REVIEW-ME : We want Day-of-Year, not of-Month!
                for idx, value in enumerate(statistics[key]):
                    day_of_year = idx + 1  # index to day of year
                    table.add_row(f"Day {day_of_year}", str(value))
                table.add_row("", "")

    if custom_freq_label and custom_freq_label in statistics:
        custom_freq_data = statistics[custom_freq_label]
        period_count = 1
        for value in custom_freq_data:
            label = f"{groupby} Period {period_count}"
            table.add_row(label, str(value))
            period_count += 1
        table.add_row("", "")

    # Index of
    for key, value in statistics.items():
        if key in index_metadata:
            # table.add_row(key, str(round_float_values(value, rounding_places)))
            table.add_row(key, str(value))

    from rich.panel import Panel
    panel = Panel(table, title="Statistics", expand=False)
    console = Console()
    console.print(panel)


def export_statistics_to_csv(data_array, filename):
    statistics = calculate_series_statistics(data_array)
    with open(f'{filename}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Statistic", "Value"])
        for statistic, value in statistics.items():
            writer.writerow([statistic, value])
