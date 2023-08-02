from devtools import debug
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import numpy as np
from bokeh.embed import components
from bokeh.embed import json_item
from bokeh.io import show
from bokeh.models import Legend
from bokeh.models import LegendItem
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.plotting import save
from pvgisprototype.api.geometry.solar_declination import calculate_solar_declination
from pvgisprototype.models.hargreaves.solar_declination import calculate_solar_declination_hargreaves
from pvgisprototype.models.pvgis.solar_declination import calculate_solar_declination_pvgis


def days_in_year(year):
    start_date = datetime(year, 1, 1)  # First day of the year
    end_date = datetime(year + 1, 1, 1)  # First day of the next year
    return (end_date - start_date).days


def generate_timestamps(start_date: datetime, end_date: datetime):
    return [start_date + timedelta(days=i) for i in range((end_date - start_date).days)]


def calculate_declinations(timestamps, output_units="radians"):
    solar_declinations = np.vectorize(calculate_solar_declination)(
        timestamps, angle_output_units=output_units
    )  # output_units='degrees'

    solar_declinations_pvgis = np.vectorize(calculate_solar_declination_pvgis)(
        timestamps, angle_output_units=output_units
    )  # output_units='degrees'

    solar_declinations_hargreaves = np.vectorize(
        calculate_solar_declination_hargreaves
    )(timestamps, angle_output_units=output_units)

    return solar_declinations, solar_declinations_pvgis, solar_declinations_hargreaves
    

def plot_solar_declination(
    start_date: datetime = None,
    end_date: datetime = None,
    year: int = None,
    title: str = "Variation of Solar Declination",
    output_units: str = "radians",
):
    if year is not None:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
    elif start_date is None or end_date is None:
        raise ValueError('Either `start_date` and `end_date` or only `year` should be provided')

    timestamps = generate_timestamps(start_date, end_date)
    solar_declinations, solar_declinations_pvgis, solar_declinations_hargreaves = calculate_declinations(timestamps, output_units)

    fig = plt.figure(figsize=(10,6))
    # plt.plot(timestamps, solar_declinations, linewidth=4, alpha=0.7, label='PVIS', linestyle='-', color='#66CCCC')
    plt.plot(timestamps, solar_declinations, linewidth=4, alpha=0.7, label='PVIS', linestyle='-', color='#00BFFF')
    plt.plot(timestamps, solar_declinations_pvgis, linewidth=2.0, alpha=0.35, label='PVGIS (current C code)', linestyle='--', color='red')
    plt.plot(timestamps, solar_declinations_hargreaves, linewidth=2.0, alpha=1.0, label='Hargreaves', linestyle=':', color='#9966CC')
    plt.xlabel('Day of the Year')
    plt.ylabel(f'{output_units}')
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.savefig(f'solar_declination_{start_date.year}_to_{end_date.year}.png')
    return fig


def plot_solar_declination_five_years(
    start_year: int,
    title: str = "Five-Year Variation of Solar Declination",
    output_units: str = "radians",
):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(start_year + 5, 1, 1)
    fig = plot_solar_declination(
        start_date=start_date, end_date=end_date, title=title, output_units=output_units
    )
    # fig.savefig(f"solar_declination_{start_year}_to_{end_date.year}.png")
    return fig


def plot_solar_declination_one_year_bokeh(
        year: int,
        title: str = 'Annual Variation of Solar Declination',
        angle_output_units: str = 'radians',
        ):
    timestamps = [datetime(year, 1, 1) + timedelta(days=i) for i in range((datetime(year+1, 1, 1) - datetime(year, 1, 1)).days)]
    timestamps_float = [timestamp.toordinal() for timestamp in timestamps]  # Bokeh doesn't handle datetime
    solar_declinations = calculate_solar_declination(timestamp=timestamps, angle_output_units=angle_output_units)
    solar_declinations_pvgis = calculate_solar_declination_pvgis(timestamps, angle_output_units)
    solar_declinations_hargreaves = calculate_solar_declination_hargreaves(timestamps, angle_output_units)

    fig = figure(width=800, height=600, title=title, x_axis_type="datetime")
    p1 = fig.line(timestamps_float, solar_declinations, line_width=4, alpha=0.7, color='#00BFFF')
    p2 = fig.line(timestamps_float, solar_declinations_pvgis, line_width=2, alpha=0.35, color='red')
    p3 = fig.line(timestamps_float, solar_declinations_hargreaves, line_width=2, alpha=1, color='#9966CC')
    
    fig.xaxis.axis_label = 'Day of the Year'
    fig.yaxis.axis_label = output_units
    
    legend = Legend(items=[
        LegendItem(label='PVIS', renderers=[p1]),
        LegendItem(label='PVGIS (current C code)', renderers=[p2]),
        LegendItem(label='Hargreaves', renderers=[p3])
    ])
    fig.add_layout(legend)
    fig.legend.location = "top_left"

    fig.grid.grid_line_color = "gray"
    fig.grid.grid_line_alpha = 0.3

    script, div = components(fig)
    return script, div
