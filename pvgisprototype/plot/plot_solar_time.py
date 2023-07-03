from devtools import debug
import logging
import matplotlib.pyplot as plt
from bokeh.embed import components
from bokeh.models import Legend
from bokeh.models import Legend, LegendItem
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.plotting import save
from bokeh.plotting import show

from datetime import datetime, timedelta
# from .api.geometry.solar_time import SolarTimeModels
from pvgisprototype.api.geometry.solar_time import SolarTimeModels
from pvgisprototype.api.geometry.solar_time import model_solar_time
from pvgisprototype.api.geometry.solar_time import calculate_solar_time

import numpy as np
from rich.progress import track
import pytz


def plot_solar_time(longitude, latitude, location, timezone, model):
    timestamp = datetime.now(tz=pytz.timezone(timezone))

    theta = np.linspace(0.0, 2 * np.pi, len(SolarTimeModels), endpoint=False)
    radii = []
    labels = []

    for model in models:
        if model != SolarTimeModels.all:  # ignore 'all' in the enumeration
            solar_time, unit = model_solar_time(longitude, latitude, timestamp, timezone, model)
            radii.append(solar_time)
            labels.append(model.name)

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, polar=True)  # 111 : 1x1 grid, first subplot

    bars = ax.bar(theta, radii, width=0.4, bottom=0.0)
    # Use custom colors and opacity
    for r, bar, label in zip(radii, bars, labels):
        bar.set_facecolor(plt.cm.viridis(r / 24.))  # range in [0,24] hours
        bar.set_alpha(0.8)
        bar.set_label(label)

    ax.set_yticklabels([])
    ax.set_xticks(theta)
    ax.set_xticklabels(labels, fontsize=8)

    plt.title(f'Solar Time for {location} at {timestamp.strftime("%Y-%m-%d %H:%M:%S")}', y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    fig.savefig(f'solar_time_comparison_at_{longitude}_{latitude}.png')

    return fig


def plot_solar_time_one_year(
        longitude,
        latitude,
        timezone,
        year,
        models,
        location,
    ):
    timezone = pytz.timezone(timezone)
    timestamps = [datetime(year, 1, 1, tzinfo=timezone) + timedelta(days=i) for i in range((datetime(year+1, 1, 1, tzinfo=timezone) - datetime(year, 1, 1, tzinfo=timezone)).days)]

    results = {}
    for model in track(models, description=f'Models {models}'):
        if model != SolarTimeModels.all:  # ignore 'all' in the enumeration
            solar_times = []
            for timestamp in timestamps:
                solar_time, unit = model_solar_time(longitude, latitude, timestamp, timezone, model)
                solar_times.append(solar_time)
            results[model.value] = {'location': location, 'timezone': timezone, 'year': year, 'solar_times': solar_times, 'unit': unit}  # Add model solar_times to results

    plt.figure(figsize=(10, 6))

    for model, data in results.items():
        solar_times = data['solar_times']
        plt.plot(timestamps, solar_times, label=model)

    # plt.xlabel('Day of the Year')
    plt.ylabel('decimal hours')
    plt.title(f'Variation of Solar Time at {location} in {year}')
    plt.legend()
    plt.grid(True)

    plt.savefig(f'solar_time_at_{location}_{year}.png')


def plot_solar_time_one_year_bokeh_static(
        longitude,
        latitude,
        timezone,
        year,
        models,
        location,
    ):
    timezone = pytz.timezone(timezone)
    timestamps = [datetime(year, 1, 1, tzinfo=timezone) + timedelta(days=i) for i in range((datetime(year+1, 1, 1, tzinfo=timezone) - datetime(year, 1, 1, tzinfo=timezone)).days)]

    results = {}
    for model in track(models, description=f'Models {models}'):
        if model != SolarTimeModels.all:  # ignore 'all' in the enumeration
            solar_times = []
            for timestamp in timestamps:
                solar_time, unit = model_solar_time(longitude, latitude, timestamp, timezone, model)
                solar_times.append(solar_time)
            results[model.value] = {'location': location, 'timezone': timezone, 'year': year, 'solar_times': solar_times, 'unit': unit}  # Add model solar_times to results

    # output to static HTML file
    output_file(f"solar_time_at_{location}_{year}.html")

    p = figure(x_axis_type='datetime', width=800, height=350, title=f'Variation of Solar Time at {location} in {year}')
    legend_items = []

    for model, data in results.items():
        solar_times = data['solar_times']
        line = p.line(timestamps, solar_times, line_width=2)
        legend_items.append((model, [line]))

    # add a legend
    legend = Legend(items=legend_items)
    p.add_layout(legend, 'right')

    show(p)


def plot_solar_time_one_year_bokeh(
        longitude,
        latitude,
        timezone,
        year,
        models,
        location,
        ):
    # debug(locals())
    timestamps = [datetime(year, 1, 1) + timedelta(days=i) for i in range((datetime(year+1, 1, 1) - datetime(year, 1, 1)).days)]
    timestamps_float = [timestamp.toordinal() for timestamp in timestamps]  # Bokeh doesn't handle datetime

    results = {}
    for model in track(models, description = f'Model : {model}'):
        # print(f'Model : {model}')
        print(f'Model in class ? : {SolarTimeModels(model)}')
        if model != SolarTimeModels.all:  # ignore 'all' in the enumeration
            model_results = []
            for timestamp in timestamps:
                solar_time, unit = model_solar_time(longitude, latitude, timestamp, timezone, SolarTimeModels(model))
                model_results.append(solar_time)
            results[model.value] = model_results

    title = f'Annual Variation of Solar Time at {location}',
    fig = figure(width=800, height=600, title=title, x_axis_type="datetime")

    renderers = []
    for model_name, solar_time in results.items():
        p = fig.line(timestamps_float, solar_time, line_width=2, alpha=0.7, color=Category20[len(results)][i])
        renderers.append(p)

    fig.xaxis.axis_label = 'Day of the Year'
    fig.yaxis.axis_label = 'Solar Time (hours)'

    legend = Legend(items=[LegendItem(label=model_name, renderers=[renderer]) for model_name, renderer in zip(results.keys(), renderers)])
    fig.add_layout(legend)
    fig.legend.location = "top_left"

    fig.grid.grid_line_color = "gray"
    fig.grid.grid_line_alpha = 0.3

    script, div = components(fig)
    save(fig, filename=f'solar_time_{location}.png')
    return script, div
