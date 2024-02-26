from devtools import debug
from rich.console import Console
import xarray as xr
import numpy as np
from scipy.stats import mode
from rich.table import Table
from rich import box
import csv
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT


def calculate_series_statistics(
        data_array,
        timestamps,
        groupby: str = None,
):
    """ """
    import xarray as xr
    if isinstance(data_array, dict):
        data_array = list(data_array.values())[0]  # Review Me !  Improve Me !
    data_xarray = xr.DataArray(
        data_array,
        coords=[('time', timestamps)],
        name='Effective irradiance series'
    )
    data_xarray.attrs['units'] = 'W/m^2'
    data_xarray.attrs['long_name'] = 'Effective Solar Irradiance'
    data_xarray.load()
    statistics = {
        'Start': data_xarray.time.values[0],
        'End': data_xarray.time.values[-1],
        'Count': data_xarray.count().values,
        'Min': data_xarray.min().values,
        '25th Percentile': np.percentile(data_xarray, 25),
        'Mean': data_xarray.mean().values,
        'Median': data_xarray.median().values,
        'Mode': mode(data_xarray.values.flatten())[0],
        'Max': data_xarray.max().values,
        'Sum': data_xarray.sum().values,
        'Variance': data_xarray.var().values,
        'Standard deviation': data_xarray.std().values,
        'Time of Min': data_xarray.idxmin('time').values,
        'Index of Min': data_xarray.argmin().values,
        'Time of Max': data_xarray.idxmax('time').values,
        'Index of Max': data_xarray.argmax().values,
        # 'Longitude of Max': data_xarray.argmax('lon').values,
        # 'Latitude of Max': data_xarray.argmax('lat').values,
    }
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
        else:
            statistics[label] = data_xarray.resample(time=freq).mean().values

    elif groupby:  # custom frequencies like '3H', '2W', etc.
        custom_label = f'{groupby} means'
        statistics[custom_label] = data_xarray.resample(time=groupby).mean().values

    return statistics

# def print_series_statistics(statistics):
#     table = Table(title="Descriptive Statistics")

#     table.add_column("Statistic", justify="right", style="cyan", no_wrap=True)
#     table.add_column("Value", style="magenta")

#     for statistic, value in statistics.items():
#         table.add_row(statistic, str(value))

#     console = Console()
#     console.print(table)


def print_series_statistics(
    data_array,
    timestamps,
    title='Time series',
    groupby: str = None,
    rounding_places: int = None,
):
    """
    """
    statistics = calculate_series_statistics(data_array, timestamps, groupby)
    table = Table(
        title=title,
        caption='Caption text',
        show_header=True,
        header_style="bold magenta",
        row_styles=['none', 'dim'],
        box=box.SIMPLE_HEAD,
        highlight=True,
    )
    table.add_column("Statistic", justify="right", style="magenta", no_wrap=True)
    table.add_column("Value", style="cyan")

    # Basic metadata
    basic_metadata = ["Start", "End", "Count"]
    for key in basic_metadata:
        if key in statistics:
            table.add_row(key, str(statistics[key]))

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
        ]

    # Index of items
    index_metadata = [
        'Time of Min',
        'Index of Min',
        'Time of Max',
        'Index of Max', 
        ]

    # Add statistics
    for key, value in statistics.items():
        if key not in basic_metadata and key not in time_groupings and key not in index_metadata:
            # table.add_row(key, str(round_float_values(value, rounding_places)))
            table.add_row(key, str(value))

    # Separate!
    table.add_row("", "")

    # Groups
    custom_freq_label = f'{groupby} means' if groupby and groupby not in time_groupings else None
    for key, value in statistics.items():
        if key in time_groupings:

            if key == 'Monthly means':
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


    console = Console()
    console.print(table)


def export_statistics_to_csv(data_array, filename):
    statistics = calculate_series_statistics(data_array)
    with open(f'{filename}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Statistic", "Value"])
        for statistic, value in statistics.items():
            writer.writerow([statistic, value])
