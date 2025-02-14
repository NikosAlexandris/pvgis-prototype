from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pytz
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Legend, LegendItem, RangeTool
from bokeh.plotting import figure, output_file, save, show
from rich.progress import track

from pvgisprototype.api.geometry.models import SolarTimeModel, select_models
from pvgisprototype.api.geometry.solar_time import model_solar_time


def plot_solar_time(longitude, latitude, location, timezone, model):
    timestamp = datetime.now(tz=pytz.timezone(timezone))

    theta = np.linspace(0.0, 2 * np.pi, len(SolarTimeModel), endpoint=False)
    radii = []
    labels = []

    solar_time_models = select_models(
        SolarTimeModel, solar_time_model
    )  # Using a callback fails!
    for solar_time_model in solar_time_models:
        solar_time, unit = model_solar_time(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            solar_time_model=solar_time_model,
        )
        radii.append(solar_time)
        labels.append(model.name)

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, polar=True)  # 111 : 1x1 grid, first subplot

    bars = ax.bar(theta, radii, width=0.4, bottom=0.0)
    # Use custom colors and opacity
    for r, bar, label in zip(radii, bars, labels):
        bar.set_facecolor(plt.cm.viridis(r / 24.0))  # range in [0,24] hours
        bar.set_alpha(0.8)
        bar.set_label(label)

    ax.set_yticklabels([])
    ax.set_xticks(theta)
    ax.set_xticklabels(labels, fontsize=8)

    plt.title(
        f'Solar Time for {location} at {timestamp.strftime("%Y-%m-%d %H:%M:%S")}', y=1.1
    )
    plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    fig.savefig(f"solar_time_comparison_at_{longitude}_{latitude}.png")

    return fig


styles_for_solar_time_one_year = {
    "EoT": {"color": "#00BFFF", "linewidth": 3, "linestyle": "--"},
    "NOAA": {"color": "green", "linewidth": 4, "linestyle": "-."},
    "PVGIS": {"color": "red", "linewidth": 5, "linestyle": ":"},
    "Skyfield": {"color": "#9966CC", "linewidth": 6, "linestyle": ":"},
}


def plot_solar_time_one_year(
    longitude,
    latitude,
    timezone,
    year,
    models,
    location,
):
    print(f"Location : {location}")
    timezone = pytz.timezone(timezone)
    timestamps = [
        datetime(year, 1, 1, tzinfo=timezone) + timedelta(days=i)
        for i in range(
            (
                datetime(year + 1, 1, 1, tzinfo=timezone)
                - datetime(year, 1, 1, tzinfo=timezone)
            ).days
        )
    ]

    results = {}
    solar_time_models = select_models(
        SolarTimeModel, solar_time_model
    )  # Using a callback fails!
    for solar_time_model in solar_time_models:
        solar_times = []
        for timestamp in track(
            timestamps, description=f"Calculating solar time after {solar_time_model}"
        ):
            solar_time, unit = model_solar_time(
                longitude, latitude, timestamp, timezone, solar_time_model
            )
            solar_times.append(solar_time)
        results[solar_time_model.value] = {
            "location": location,
            "timezone": timezone,
            "year": year,
            "solar_times": solar_times,
            "unit": unit,
        }  # Add model solar_times to results

    plt.figure(figsize=(10, 6))

    for model, data in track(
        results.items(), description=f"Plotting data after {model}"
    ):
        solar_times = data["solar_times"]
        plt.plot(
            timestamps,
            solar_times,
            label=model,
            **styles_for_solar_time_one_year[model],
        )

    # plt.xlabel('Day of the Year')
    plt.ylabel("decimal hours")
    plt.title(f"Variation of Solar Time at {location} in {year}")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"solar_time_at_{location}_{year}.png")


styles_for_solar_time_one_year_bokeh_static = {
    "EoT": {"line_color": "#00BFFF", "line_width": 3, "line_dash": "dashed"},
    "NOAA": {"line_color": "green", "line_width": 4, "line_dash": "dotdash"},
    "PVGIS": {"line_color": "red", "line_width": 5, "line_dash": "dotted"},
    "Skyfield": {"line_color": "#9966CC", "line_width": 6, "line_dash": "dotted"},
}


def plot_solar_time_one_year_bokeh_static(
    longitude,
    latitude,
    timezone,
    year,
    models,
    location,
):
    # Get the timezone right!
    timezone = pytz.timezone(timezone)

    # Build the time series
    timestamps = [
        datetime(year, 1, 1, tzinfo=timezone) + timedelta(days=i)
        for i in range(
            (
                datetime(year + 1, 1, 1, tzinfo=timezone)
                - datetime(year, 1, 1, tzinfo=timezone)
            ).days
        )
    ]

    # Create a dictionary for the source data
    source_data = {"timestamps": timestamps}

    # Calculate and collect solar times for each model
    results = {}
    solar_time_models = select_models(
        SolarTimeModel, solar_time_model
    )  # Using a callback fails!
    for solar_time_model in solar_time_models:
        solar_times = []
        for timestamp in track(
            timestamps, description="Calculating solar time after {solar_time_model}"
        ):
            solar_time, unit = model_solar_time(
                longitude, latitude, timestamp, timezone, solar_time_model
            )
            solar_times.append(solar_time)
        results[solar_time_model.value] = {
            "location": location,
            "timezone": timezone,
            "year": year,
            "solar_times": solar_times,
            "unit": unit,
        }  # Add model solar_times to results
        source_data[solar_time_model.value] = (
            solar_times  # Add model solar_times to source data
        )

    # Define the `source`
    source = ColumnDataSource(source_data)

    # Initialise the figure
    p = figure(
        x_axis_type="datetime",
        title=f"Variation of Solar Time at {location} in {year}",
        width=800,
    )

    # A list for
    legend_items = []

    # Plot
    for model, data in track(
        results.items(), description=f"Plotting solar times after {model}"
    ):
        style = styles_for_solar_time_one_year_bokeh_static.get(
            model, {"line_color": "black", "line_width": 2, "line_dash": "solid"}
        )  # if model style not defined, use the latter one

        line = p.line(
            "timestamps",
            model,
            source=source,
            line_color=style["line_color"],
            line_width=style["line_width"],
            line_dash=style["line_dash"],
        )

        legend_items.append((model, [line]))

    # Add the legend
    legend = Legend(items=legend_items)
    p.add_layout(legend, "right")

    #
    select = figure(
        title="Drag the middle and edges of the selection box to change the range above",
        height=130,
        width=800,
        x_axis_type="datetime",
        x_range=(timestamps[100], timestamps[200]),
        x_axis_location="above",
        y_axis_type=None,
        tools="xpan",
        toolbar_location=None,
        background_fill_color="#efefef",
    )

    #
    range_tool = RangeTool(x_range=p.x_range)
    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.2

    # Create the range tool plot
    for model in results.keys():
        select.line("timestamps", model, source=source, color="gray")

    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)

    # Output to static HTML file
    output_file(f"solar_time_at_{location}_{year}.html")

    # Show both plots
    show(column(p, select))


def plot_solar_time_one_year_bokeh(
    longitude,
    latitude,
    timezone,
    year,
    models,
    location,
):
    timestamps = [
        datetime(year, 1, 1) + timedelta(days=i)
        for i in range((datetime(year + 1, 1, 1) - datetime(year, 1, 1)).days)
    ]
    timestamps_float = [
        timestamp.toordinal() for timestamp in timestamps
    ]  # Bokeh doesn't handle datetime

    results = {}
    solar_time_models = select_models(
        SolarTimeModel, solar_time_model
    )  # Using a callback fails!
    for solar_time_model in solar_time_models:
        model_results = []
        for timestamp in timestamps:
            solar_time, unit = model_solar_time(
                longitude,
                latitude,
                timestamp,
                timezone,
                SolarTimeModel(solar_time_model),
            )
            model_results.append(solar_time)
        results[solar_time_model.value] = model_results

    title = (f"Annual Variation of Solar Time at {location}",)
    fig = figure(width=800, height=600, title=title, x_axis_type="datetime")

    renderers = []
    for model_name, solar_time in results.items():
        p = fig.line(
            timestamps_float,
            solar_time,
            line_width=2,
            alpha=0.7,
            color=Category20[len(results)][i],
        )
        renderers.append(p)

    fig.xaxis.axis_label = "Day of the Year"
    fig.yaxis.axis_label = "Solar Time (hours)"

    legend = Legend(
        items=[
            LegendItem(label=model_name, renderers=[renderer])
            for model_name, renderer in zip(results.keys(), renderers)
        ]
    )
    fig.add_layout(legend)
    fig.legend.location = "top_left"

    fig.grid.grid_line_color = "gray"
    fig.grid.grid_line_alpha = 0.3

    script, div = components(fig)
    save(fig, filename=f"solar_time_{location}.png")
    return script, div
