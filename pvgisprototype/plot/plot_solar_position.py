import logging
from datetime import datetime, time, timedelta, timezone
from typing import List
import matplotlib.pyplot as plt
import numpy as np
from pvgisprototype.algorithms.pvgis.solar_geometry import (
    calculate_solar_position_pvgis,
)
from pvgisprototype.api.geometry.models import SolarPositionModel
from pvgisprototype.api.geometry.overview import model_solar_geometry_overview
from pvgisprototype.constants import ALTITUDE_NAME, AZIMUTH_NAME
# from pvgisprototype.api.geometry.solar_position import calculate_solar_geometry_overview
# from pvgisprototype.algorithms.skyfield.solar_geometry import calculate_solar_position_skyfield
# from pvgisprototype.validation.data_structures import SolarGeometryDayConstants
# from pvgisprototype.validation.data_structures import SolarGeometryDayVariables


logging.basicConfig(
    level=logging.DEBUG,
    # level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("error.log"),  # Save log to a file
        logging.StreamHandler(),  # Print log to the console
    ],
)

def plot_daily_solar_altitude(
    longitude: float,
    latitude: float,
    day: datetime,
    model: SolarPositionModel,
    title: str = "Daily Variation of Solar Position",
    solar_geometry_day_constants=None,
    year=None,
    hour_of_year=None,
):
    timestamps = [
        day.replace(hour=h, minute=0, second=0, microsecond=0) for h in range(24)
    ]
    altitudes = []

    for timestamp in timestamps:
        if model == calculate_solar_position_pvgis:
            solar_altitude, _, _ = model(
                solar_geometry_day_constants, year, hour_of_year
            )
            altitudes.append(solar_altitude)
        else:
            solar_altitude, _, units = model_solar_geometry_overview(
                longitude, latitude, timestamp, model
            )
            altitudes.append(solar_altitude)

    fig, ax = plt.subplots()

    # Remove unwanted spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_xlabel("Hour of the day")
    ax.set_ylabel("Solar Altitude")
    ax.plot(timestamps, altitudes)
    # plt.tick_params(axis='y')

    plt.suptitle(title)
    subtitle = f" observed from (longitude, latitude) {longitude}, {latitude}"
    subtitle += f" based on {model}"
    ax.set_title(subtitle)
    plt.savefig(f"solar_altitude_daily_{model}.png")


def plot_daily_solar_azimuth(
    longitude: float,
    latitude: float,
    day: datetime,
    model: SolarPositionModel,
    title: str = "Daily Variation of Solar Position",
):
    azimuths = []
    azimuths = []
    timestamps = [
        day.replace(hour=h, minute=0, second=0, microsecond=0) for h in range(24)
    ]
    for timestamp in timestamps:
        altitude, azimuth, units = model_solar_geometry_overview(
            longitude, latitude, timestamp, model
        )
        azimuths.append(azimuth)

    fig, ax = plt.subplots()

    # Remove unwanted spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.xlabel("Hour of the day")
    plt.ylabel("Solar Azimuth")
    plt.plot(timestamps, azimuths)
    # plt.tick_params(axis='y')

    plt.suptitle(title)
    title = f" observed from (longitude, latitude) {longitude}, {latitude}"
    title = f" based on {model}"
    plt.title(title)
    plt.savefig(f"solar_azimuth_daily_{model}.png")


def plot_daily_solar_position(
    longitude: float,
    latitude: float,
    timestamp: datetime,
    model: SolarPositionModel,
    title: str = "Daily Variation of Solar Position",
):
    altitudes = []
    azimuths = []
    timestamps = [
        timestamp.replace(hour=h, minute=0, second=0, microsecond=0) for h in range(24)
    ]
    for timestamp in timestamps:
        altitude, azimuth, units = model_solar_geometry_overview(
            longitude, latitude, timestamp, model
        )
        logging.debug(f"{model}: Altitude={altitude}, Azimuth={azimuth}")
        altitudes.append(altitude)
        azimuths.append(azimuth)

    fig, ax1 = plt.subplots()

    # Remove unwanted spines
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # color = 'tab:red'
    ax1.set_xlabel("Hour of the day")
    # ax1.set_ylabel(ALTITUDE_NAME, color=color)
    ax1.set_ylabel(ALTITUDE_NAME)
    # ax1.plot(timestamps, altitudes, color=color)
    ax1.plot(timestamps, altitudes)
    # ax1.tick_params(axis='y', labelcolor=color)
    ax1.tick_params(axis="y")

    ax2 = ax1.twinx()

    # Remove unwanted spines
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # color = 'tab:blue'
    # ax2.set_ylabel(AZIMUTH_NAME, color=color)
    ax2.set_ylabel(AZIMUTH_NAME)
    # ax2.plot(range(24), azimuths, color=color)
    # ax2.plot(timestamps, azimuths, color=color)
    ax2.plot(timestamps, azimuths)
    # ax2.tick_params(axis='y', labelcolor=color)
    ax2.tick_params(axis="y")

    # fig.tight_layout()
    title += f" based on {model}"
    plt.title(title)
    plt.savefig(f"solar_position_daily_{model}.png")


def plot_daily_solar_position_models(
    longitude: float,
    latitude: float,
    day: datetime,
    models: List[SolarPositionModel],
    title: str = "Daily Variation of Solar Position",
):
    timestamps = [
        day.replace(hour=h, minute=0, second=0, microsecond=0) for h in range(24)
    ]

    fig, axs = plt.subplots(
        len(models), 1, figsize=(8, len(models) * 6)
    )  # adjust the figure size as needed

    for i, model in enumerate(models):
        altitudes = []
        azimuths = []
        for timestamp in timestamps:
            altitude, azimuth, units = model_solar_geometry_overview(
                longitude, latitude, timestamp, timezone, model
            )
            altitudes.append(altitude)
            azimuths.append(azimuth)

        ax1 = axs[i]
        ax1.set_xlabel("Hour of the day")
        ax1.set_ylabel(ALTITUDE_NAME)
        ax1.plot(timestamps, altitudes)

        ax2 = ax1.twinx()
        ax2.set_ylabel(AZIMUTH_NAME)
        ax2.plot(timestamps, azimuths)

        ax1.title.set_text(f"{title} - Model: {model.value}")

    # plt.tight_layout()
    plt.savefig("solar_position_daily_comparison.png")


def plot_daily_solar_position_scatter(
    longitude: float,
    latitude: float,
    day: datetime,
    model: SolarPositionModel,
    title: str = "Daily Variation of Solar Position",
):
    altitudes = []
    azimuths = []
    timestamps = [
        day.replace(hour=h, minute=0, second=0, microsecond=0) for h in range(24)
    ]
    for timestamp in timestamps:
        altitude, azimuth, units = model_solar_geometry_overview(
            longitude, latitude, timestamp, model
        )
        altitudes.append(altitude)
        azimuths.append(azimuth)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Remove unwanted spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.scatter(azimuths, altitudes, label="Solar Geometry Plot")
    plt.xlabel(AZIMUTH_NAME)
    plt.ylabel(ALTITUDE_NAME)

    # fig.tight_layout()
    plt.title(title)
    plt.savefig(f"solar_geometry_daily_{model}.png")


def plot_yearly_solar_position(
    longitude: float,
    latitude: float,
    year: int,
    model: SolarPositionModel,
):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    delta = timedelta(days=1)
    timestamps = []
    altitudes = []
    azimuths = []

    while start_date <= end_date:
        timestamp = datetime.combine(start_date, time(12, 0))
        altitude, azimuth = model_solar_geometry_overview(
            longitude, latitude, timestamp, model
        )
        timestamps.append(start_date)
        altitudes.append(altitude)
        azimuths.append(azimuth)
        start_date += delta

    fig, ax1 = plt.subplots()

    # Remove unwanted spines
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    color = "tab:red"
    ax1.set_xlabel("Day of the year")
    ax1.set_ylabel(ALTITUDE_NAME, color=color)
    ax1.plot(timestamps, altitudes, color=color)
    ax1.tick_params(axis="y", labelcolor=color)

    ax2 = ax1.twinx()
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    color = "tab:blue"
    ax2.set_ylabel(AZIMUTH_NAME, color=color)
    ax2.plot(timestamps, azimuths, color=color)
    ax2.tick_params(axis="y", labelcolor=color)

    fig.tight_layout()
    plt.title(f"Sun Position in {start_date}")
    plt.savefig("solar_position_yearly.png")


def plot_analemma(longitude, latitude, year, model):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    delta = timedelta(hours=1)
    timestamps = []
    azimuths = []
    zeniths = []

    while start_date <= end_date:
        for h in range(24):
            timestamp = datetime.combine(start_date, time(h, 0))
            altitude, azimuth = model_solar_geometry_overview(
                longitude, latitude, timestamp, model
            )
            if altitude > 0:  # consider only daytime
                timestamps.append(timestamp)
                azimuths.append(azimuth)
                zeniths.append(90 - altitude)  # from altitude to zenith
        start_date += delta

    fig = plt.figure()
    ax = plt.subplot(1, 1, 1, projection="polar")

    # draw analemmas
    points = ax.scatter(
        np.radians(azimuths),
        zeniths,
        s=2,
        c=[t.timetuple().tm_yday for t in timestamps],
    )
    fig.colorbar(points)

    # draw hour labels
    for hour in np.unique([t.hour for t in timestamps]):
        subset_indices = [i for i, t in enumerate(timestamps) if t.hour == hour]
        subset_zeniths = [zeniths[i] for i in subset_indices]
        pos_index = subset_indices[
            subset_zeniths.index(min(subset_zeniths))
        ]  # smallest zenith for each hour
        ax.text(np.radians(azimuths[pos_index]), zeniths[pos_index], str(hour))

    # draw individual days
    for month, day in [(3, 21), (6, 21), (12, 21)]:
        date = datetime(year, month, day)
        times_indices = [i for i, t in enumerate(timestamps) if t.date() == date]
        if times_indices:
            azimuths_date = [azimuths[i] for i in times_indices]
            zeniths_date = [zeniths[i] for i in times_indices]
            ax.plot(
                np.radians(azimuths_date), zeniths_date, label=date.strftime("%Y-%m-%d")
            )

    ax.legend(loc="upper left")

    # compass-like view
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rmax(90)
    plt.savefig(f"solar_analemma_{model}.png")
