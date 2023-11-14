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
    # Aggregate statistics based on frequency
    if groupby == 'Y':
        statistics['Yearly means'] = data_xarray.groupby('time.year').mean().values
    if groupby == 'M':
        statistics['Monthly means'] = data_xarray.groupby('time.month').mean().values
    elif groupby == 'D':
        statistics['Daily means'] = data_xarray.groupby('time.day').mean().values
    if groupby == 'W':
        statistics['Weekly means'] = data_xarray.resample(time='1W').mean().values
    if groupby == 'S':
        statistics['Seasonal means'] = data_xarray.groupby('time.season').mean().values

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
    groups = [
        'Monthly means',
        'Daily means',
        'Weekly means',
        'Seasonal means',
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
        if key not in basic_metadata and key not in groups and key not in index_metadata:
            # table.add_row(key, str(round_float_values(value, rounding_places)))
            table.add_row(key, str(value))

    # Separate!
    table.add_row("", "")

    # Groups
    for key, value in statistics.items():
        if key in groups:

            if key == 'Monthly means':
                import calendar
                for idx, value in enumerate(statistics[key], start=1):
                    month_name = calendar.month_name[idx]  # Get month name
                    # table.add_row(key, str(round_float_values(value, rounding_places)))
                    table.add_row(month_name, str(value))
                table.add_row("", "")

            if key == 'Daily means':  # REVIEW-ME : We want Day-of-Year, not of-Month!
                for idx, value in enumerate(statistics[key]):
                    day_of_year = idx + 1  # Convert index to day of the year
                    table.add_row(f"Day {day_of_year}", str(value))
                table.add_row("", "")

            if key == 'Weekly means':
                for idx, value in enumerate(statistics[key]):
                    week_number = idx + 1  # Week number
                    table.add_row(f"Week {week_number}", str(value))
                table.add_row("", "")

            if key == 'Seasonal means':
                seasons = ['DJF', 'MAM', 'JJA', 'SON']  # Define the seasons
                for season, value in zip(seasons, statistics[key]):
                    table.add_row(season, str(value))
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
