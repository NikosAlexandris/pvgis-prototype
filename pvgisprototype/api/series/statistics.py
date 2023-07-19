from devtools import debug
from rich.console import Console
import xarray as xr
import numpy as np
from scipy.stats import mode
from rich.table import Table
import csv


def calculate_series_statistics(data_array):
    data_array.load()
    statistics = {
        'Count': data_array.count().values,
        'Min': data_array.min().values,
        'Mean': data_array.mean().values,
        'Median': data_array.median().values,
        'Mode': mode(data_array.values.flatten())[0],
        'Max': data_array.max().values,
        'Variance': data_array.var().values,
        'Standard deviation': data_array.std().values,
        'Sum': data_array.sum().values,
        'Max value index': data_array.argmax().values,
        # 'Max value longitude': data_array.argmax('lon').values,
        # 'Max value latitude': data_array.argmax('lat').values,
        'Max value time': data_array.idxmax('time').values,
        'Min value index': data_array.argmin().values,
        'Min value time': data_array.idxmin().values,
        # sum = location_time_series.where(location_time_series > 0).sum()
        # '25th Percentile': np.percentile(data_array, 25),
    }
    return statistics


def print_series_statistics(statistics):
    table = Table(title="Descriptive Statistics")

    table.add_column("Statistic", justify="right", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    for statistic, value in statistics.items():
        table.add_row(statistic, str(value))

    console = Console()
    console.print(table)


def export_statistics_to_csv(statistics, filename):
    with open(f'{filename}.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Statistic", "Value"])
        for statistic, value in statistics.items():
            writer.writerow([statistic, value])

