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


def calculate_series_statistics(
    data_array: np.array,
    timestamps: DatetimeIndex,
    groupby: str = None,
) -> dict:
    """ """
    import xarray as xr
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

    # Regardless of whether the input data_array is a array or a dict :
    data_xarray = xr.DataArray(
        data_array,
        coords=[('time', timestamps)],
        name='Effective irradiance series'
    )
    data_xarray.attrs['units'] = 'W/m^2'
    data_xarray.attrs['long_name'] = 'Photovoltaic power'
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
        'Sum of Group Means': float,
    }
    time_groupings = {
        'Y': ('year', 'Yearly means'),
        'S': ('season', 'Seasonal means'),
        'M': ('month', 'Monthly means'),
        'W': ('1W', 'Weekly means'),
        'D': ('1D', 'Daily means'),
        'H': ('1H', 'Hourly means'),
    }
    print(f'Groupby : {groupby}')
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
    data_array: np.array,
    timestamps: DatetimeIndex,
    title: str ='Time series',
    groupby: str = None,
    yearly_overview: bool = False,
    rounding_places: int = None,
    verbose=1,
) -> None:
    """
    """
    rename_yearly_output_rows = {
        "Sum of Group Means": "Yearly PV energy",
        f"Sum of {GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME}": 'Yearly in-plane irradiance',
    }
    if groupby and groupby.lower() == 'yearly':
        yearly_overview = True

    table = Table(
        title=title,
        caption='Caption text',
        show_header=True,
        header_style="bold magenta",
        row_styles=['none', 'dim'],
        box=box.SIMPLE_HEAD,
        highlight=True,
    )
    if yearly_overview:  # typical overview !
        table.add_column("Statistic", justify="right", style="bright_blue", no_wrap=True)
        table.add_column("Value", style="cyan")
        # get monthly mean values
        statistics = calculate_series_statistics(data_array, timestamps, 'M')
    else:
        table.add_column("Statistic", justify="right", style="magenta", no_wrap=True)
        table.add_column("Value", style="cyan")
        statistics = calculate_series_statistics(data_array, timestamps, groupby)

    # Basic metadata
    if not yearly_overview:
        basic_metadata = ["Start", "End", "Count"]
    else:
        basic_metadata = ["Start", "End"]
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
        groupby + ' means' if groupby else None,  # do not print custom frequency means
        ]

    if yearly_overview:
        yearly_metadata = [
                # 'Min',
                # 'Mean',
                # 'Max',
                # 'Standard deviation',
                'Sum of Group Means',
                'Irradiance',
               f"Sum of {GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME}",
            ]

    # Index of items
    if not yearly_overview:
        index_metadata = [
            'Time of Min',
            'Index of Min',
            'Time of Max',
            'Index of Max', 
            ]
    else:
        index_metadata = [
            # 'Time of Min',
            # 'Time of Max',
            ]

    # Add statistics
    for key, value in statistics.items():
        if not yearly_overview:
            if key not in basic_metadata and key not in time_groupings and key not in index_metadata:
                # table.add_row(key, str(round_float_values(value, rounding_places)))
                table.add_row(key, str(value))
        else:
            if key in yearly_metadata and key not in basic_metadata and key not in index_metadata:
                # table.add_row(key, str(round_float_values(value, rounding_places)))
                # table.add_row(key, str(value))
                display_key = rename_yearly_output_rows.get(key, key)
                table.add_row(display_key, str(value))

    # Separate!
    table.add_row("", "")

    if yearly_overview:
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

                from termcharts import bar
                from rich.panel import Panel
                # from rich.columns import Columns
                barchart = bar(statistics[key].tolist(), title='Monthly', rich=True)
                barchart_panel = Panel(barchart, expand=True)

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

        from termcharts import bar
        from rich.panel import Panel
        # from rich.columns import Columns
        barchart = bar(custom_freq_data.tolist(), title='Periods', rich=True)
        barchart_panel = Panel(barchart, expand=True)

    # Index of
    for key, value in statistics.items():
        if key in index_metadata:
            # table.add_row(key, str(round_float_values(value, rounding_places)))
            table.add_row(key, str(value))

    console = Console()
    console.print(table)
    if custom_freq_label and custom_freq_label in statistics:
        console.print(barchart_panel)
        # console.print(Columns(barchart_panels))  # for many !


def export_statistics_to_csv(data_array, filename):
    statistics = calculate_series_statistics(data_array)
    with open(f'{filename}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Statistic", "Value"])
        for statistic, value in statistics.items():
            writer.writerow([statistic, value])
