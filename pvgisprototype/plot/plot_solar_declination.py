from datetime import datetime, timedelta
from typing import List
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import numpy as np
from bokeh.embed import components
from bokeh.models import Legend, LegendItem
from bokeh.plotting import figure

from pvgisprototype.algorithms.hargreaves.solar_declination import (
    calculate_solar_declination_hargreaves,
)
from pvgisprototype.algorithms.noaa.solar_declination import (
    calculate_solar_declination_noaa,
)
from pvgisprototype.algorithms.pvgis.solar_declination import (
    calculate_solar_declination_pvgis,
)
from pvgisprototype.api.geometry.declination import calculate_solar_declination
from pvgisprototype.constants import DECLINATION_NAME, RADIANS


def generate_timestamps(start_date: datetime, end_date: datetime):
    return [start_date + timedelta(days=i) for i in range((end_date - start_date).days)]


def calculate_declinations(
    timestamps: List, timezone: ZoneInfo = None, output_units=RADIANS
):
    solar_declinations = np.vectorize(calculate_solar_declination)(
        timestamp=timestamps,
        timezone=ZoneInfo("UTC"),
        # declination_models=[SolarDeclinationModel.noaa],
        angle_output_units=output_units,  # in degrees
    )
    # restructure for plotting
    solar_declinations = [item[0][DECLINATION_NAME] for item in solar_declinations]

    solar_declinations_pvgis = np.vectorize(calculate_solar_declination_pvgis)(
        timestamp=timestamps,
        angle_output_units=output_units,  # in degrees
    )
    # restructure for plotting - SolarDeclination objects with `value`, `unit` attributes
    solar_declinations_pvgis = [item.value for item in solar_declinations_pvgis]

    solar_declinations_noaa = np.vectorize(calculate_solar_declination_noaa)(
        timestamp=timestamps,
        angle_output_units=output_units,  # in degrees
    )
    # restructure for plotting - SolarDeclination objects with `value`, `unit` attributes
    solar_declinations_noaa = [item.value for item in solar_declinations_noaa]

    solar_declinations_hargreaves = np.vectorize(
        calculate_solar_declination_hargreaves
    )(
        timestamp=timestamps,
        angle_output_units=output_units,  # in degrees
    )
    # restructure for plotting
    solar_declinations_hargreaves = [
        item.value for item in solar_declinations_hargreaves
    ]

    return (
        solar_declinations,
        solar_declinations_pvgis,
        solar_declinations_noaa,
        solar_declinations_hargreaves,
    )


def plot_solar_declination(
    start_date: datetime = None,
    end_date: datetime = None,
    year: int = None,
    title: str = "Variation of Solar Declination",
    output_units: str = RADIANS,
):
    if year is not None:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
    elif start_date is None or end_date is None:
        raise ValueError(
            "Either `start_date` and `end_date` or only `year` should be provided"
        )

    timestamps = generate_timestamps(start_date, end_date)
    (
        solar_declinations,
        solar_declinations_pvgis,
        solar_declinations_noaa,
        solar_declinations_hargreaves,
    ) = calculate_declinations(timestamps, output_units)

    fig = plt.figure(figsize=(10, 6))
    # plt.plot(timestamps, solar_declinations, linewidth=4, alpha=0.7, label='PVIS', linestyle='-', color='#66CCCC')

    plt.plot(
        timestamps,
        solar_declinations,
        linewidth=4,
        alpha=0.7,
        label="PVIS",
        linestyle="-",
        color="#00BFFF",
    )
    plt.plot(
        timestamps,
        solar_declinations_pvgis,
        linewidth=2.0,
        alpha=0.35,
        label="PVGIS (current C code)",
        linestyle="--",
        color="red",
    )
    plt.plot(
        timestamps,
        solar_declinations_noaa,
        linewidth=2.0,
        alpha=0.75,
        label="NOAA",
        linestyle="--",
        color="#004600",
    )
    plt.plot(
        timestamps,
        solar_declinations_hargreaves,
        linewidth=2.0,
        alpha=1.0,
        label="Hargreaves",
        linestyle=":",
        color="#9966CC",
    )

    plt.xlabel("Day of the Year")
    plt.ylabel(f"{output_units}")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.savefig(f"solar_declination_{start_date.year}_to_{end_date.year}.png")
    return fig


def plot_solar_declination_five_years(
    start_year: int,
    title: str = "Five-Year Variation of Solar Declination",
    output_units: str = RADIANS,
):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(start_year + 5, 1, 1)
    figure = plot_solar_declination(
        start_date=start_date, end_date=end_date, title=title, output_units=output_units
    )
    # fig.savefig(f"solar_declination_{start_year}_to_{end_date.year}.png")
    return figure


def plot_solar_declination_one_year_bokeh(
    year: int,
    title: str = "Annual Variation of Solar Declination",
    angle_output_units: str = RADIANS,
):
    timestamps = [
        datetime(year, 1, 1) + timedelta(days=i)
        for i in range((datetime(year + 1, 1, 1) - datetime(year, 1, 1)).days)
    ]
    timestamps_float = [
        timestamp.toordinal() for timestamp in timestamps
    ]  # Bokeh doesn't handle datetime
    solar_declinations = calculate_solar_declination(timestamp=timestamps)
    solar_declinations_pvgis = calculate_solar_declination_pvgis(timestamps)
    # debug(locals())
    solar_declinations_hargreaves = calculate_solar_declination_hargreaves(
        timestamps, angle_output_units
    )

    fig = figure(width=800, height=600, title=title, x_axis_type="datetime")
    p1 = fig.line(
        timestamps_float, solar_declinations, line_width=4, alpha=0.7, color="#00BFFF"
    )
    p2 = fig.line(
        timestamps_float,
        solar_declinations_pvgis,
        line_width=2,
        alpha=0.35,
        color="red",
    )
    p3 = fig.line(
        timestamps_float,
        solar_declinations_hargreaves,
        line_width=2,
        alpha=1,
        color="#9966CC",
    )

    fig.xaxis.axis_label = "Day of the Year"
    fig.yaxis.axis_label = output_units

    legend = Legend(
        items=[
            LegendItem(label="PVIS", renderers=[p1]),
            LegendItem(label="PVGIS (current C code)", renderers=[p2]),
            LegendItem(label="Hargreaves", renderers=[p3]),
        ]
    )
    fig.add_layout(legend)
    fig.legend.location = "top_left"

    fig.grid.grid_line_color = "gray"
    fig.grid.grid_line_alpha = 0.3

    script, div = components(fig)
    return script, div
