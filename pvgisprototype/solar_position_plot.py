from pvgisprototype.solar_position import calculate_solar_position
from pvgisprototype.solar_position import SolarPositionModels
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from datetime import time
import numpy as np

def plot_daily_solar_position(
        longitude: float,
        latitude: float,
        day: datetime,
        model: SolarPositionModels,
        ):
    timestamps = [day.replace(hour=h, minute=0, second=0, microsecond=0) for h in range(24)]
    altitudes = []
    azimuths = []

    for timestamp in timestamps:
        altitude, azimuth = calculate_solar_position(longitude, latitude, timestamp, model)
        altitudes.append(altitude)
        azimuths.append(azimuth)

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Hour of the day')
    ax1.set_ylabel('Altitude', color=color)
    ax1.plot(range(24), altitudes, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Azimuth', color=color)
    ax2.plot(range(24), azimuths, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.savefig('solar_position_daily.png')


def plot_yearly_solar_position(
        longitude: float,
        latitude: float,
        year: int,
        model: SolarPositionModels,
        ):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    delta = timedelta(days=1)
    timestamps = []
    altitudes = []
    azimuths = []

    while start_date <= end_date:
        timestamp = datetime.combine(start_date, time(12, 0))
        altitude, azimuth = calculate_solar_position(longitude, latitude, timestamp, model)
        timestamps.append(start_date)
        altitudes.append(altitude)
        azimuths.append(azimuth)
        start_date += delta

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Day of the year')
    ax1.set_ylabel('Altitude', color=color)
    ax1.plot(timestamps, altitudes, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Azimuth', color=color)
    ax2.plot(timestamps, azimuths, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.savefig('solar_position_yearly.png')
