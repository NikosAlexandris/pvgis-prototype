from devtools import debug
from pvgisprototype.solar_declination import calculate_solar_declination
from pvgisprototype.solar_declination import calculate_solar_declination_pvgis
from pvgisprototype.solar_declination import calculate_solar_declination_hargreaves
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from datetime import timezone
from datetime import timedelta


def days_in_year(year):
    start_date = datetime(year, 1, 1)  # First day of the year
    end_date = datetime(year + 1, 1, 1)  # First day of the next year
    return (end_date - start_date).days


def plot_solar_declination(start_date: datetime, end_date: datetime, title: str = 'Annual Variation of Solar Declination'):
    timestamps = [datetime(year, 1, 1) + timedelta(days=i) for i in range(end_date - start_date).days]
    solar_declinations = np.vectorize(calculate_solar_declination)(timestamps, output_units='degrees')  # Calculate solar declination for each day
    solar_declinations_pvgis = np.vectorize(calculate_solar_declination_pvgis)(timestamps, output_units='degrees')  # Calculate solar declination for each day
    solar_declinations_hargreaves = np.vectorize(calculate_solar_declination_hargreaves)(timestamps)  # Calculate solar declination for each day

    fig = plt.figure(figsize=(10,6))
    plt.plot(timestamps, solar_declinations, linewidth=4, alpha=0.7, label='PVIS', linestyle='-', color='#66CCCC')
    plt.plot(timestamps, solar_declinations_pvgis, linewidth=2.0, alpha=0.35, label='PVGIS (current C code)', linestyle='--', color='red')
    plt.plot(timestamps, solar_declinations_hargreaves, linewidth=2.0, alpha=1.0, label='Hargreaves', linestyle=':', color='#9966CC')
    plt.xlabel('Day of the Year')
    plt.ylabel('Solar Declination')
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.savefig('solar_declination.png')
    return fig


def plot_solar_declination_one_year(
        year: int,
        title: str = 'Annual Variation of Solar Declination',
        output_units: str = 'radians',
        ):
    timestamps = [datetime(year, 1, 1) + timedelta(days=i) for i in range((datetime(2024, 1, 1) - datetime(2023, 1, 1)).days)]
    solar_declinations = np.vectorize(calculate_solar_declination)(timestamps, output_units=output_units)
    solar_declinations_pvgis= np.vectorize(calculate_solar_declination_pvgis)(timestamps, output_units=output_units)
    solar_declinations_hargreaves = np.vectorize(calculate_solar_declination_hargreaves)(timestamps, output_units=output_units)

    fig = plt.figure(figsize=(10,6))
    plt.plot(timestamps, solar_declinations, linewidth=4, alpha=0.7, label='PVIS', linestyle='-', color='#00BFFF')
    plt.plot(timestamps, solar_declinations_pvgis, linewidth=2.0, alpha=0.35, label='PVGIS (current C code)', linestyle='--', color='red')
    plt.plot(timestamps, solar_declinations_hargreaves, linewidth=2.0, alpha=1.0, label='Hargreaves', linestyle=':', color='#9966CC')
    plt.xlabel('Day of the Year')
    plt.ylabel(f'{output_units}')
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.savefig('solar_declination.png')
    return fig


def plot_solar_declination_five_years(
        start_year: int,
        end_year: int,
        title: str = 'Five-Year Variation of Solar Declination',
        output_units: str = 'radians',
        ):
    timestamps = [datetime(start_year, 1, 1) + timedelta(days=i) for i in range((datetime(end_year, 1, 1) - datetime(start_year, 1, 1)).days)]
    solar_declinations = np.vectorize(calculate_solar_declination)(
            timestamp=timestamps,
            timezone=None,
            output_units=output_units)
    solar_declinations_pvgis = np.vectorize(calculate_solar_declination_pvgis)(timestamps, output_units=output_units)
    solar_declinations_hargreaves = np.vectorize(calculate_solar_declination_hargreaves)(timestamps, output_units=output_units)

    fig = plt.figure(figsize=(10,6))
    plt.plot(timestamps, solar_declinations, linewidth=4, alpha=0.5, label='PVIS', linestyle='-', color='#00BFFF')
    plt.plot(timestamps, solar_declinations_pvgis, linewidth=2.0, alpha=0.4, label='PVGIS (current C code)', linestyle='--', color='red')
    plt.plot(timestamps, solar_declinations_hargreaves, linewidth=2.0, alpha=1.0, label='Hargreaves', linestyle=':', color='#9966CC')
    # plt.xlabel('Day of the Year')
    plt.ylabel(f'{output_units}')
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.savefig(f'solar_declination_{start_year}_to_{end_year}.png')
    return fig
