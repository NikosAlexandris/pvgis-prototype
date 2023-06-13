from devtools import debug
from pvgisprototype.solar_declination import calculate_solar_declination
from pvgisprototype.solar_declination import calculate_solar_declination_hargreaves
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


def days_in_year(year):
    start_date = datetime(year, 1, 1)  # First day of the year
    end_date = datetime(year + 1, 1, 1)  # First day of the next year
    return (end_date - start_date).days


def plot_solar_declination(title: str = 'Annual Variation of Solar Declination'):
    days = np.arange(1, 366)
    solar_declinations = np.vectorize(calculate_solar_declination)(days, output_units='degrees')  # Calculate solar declination for each day
    solar_declinations_hargreaves = np.vectorize(calculate_solar_declination_hargreaves)(days)  # Calculate solar declination for each day

    fig = plt.figure(figsize=(10,6))
    plt.plot(days, solar_declinations, label='PVGIS')
    plt.plot(days, solar_declinations_hargreaves, label='Hargreaves')
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
        ):
    days = np.arange(days_in_year(year))
    solar_declinations = np.vectorize(calculate_solar_declination)(days, output_units='degrees')  # Calculate solar declination for each day
    solar_declinations_hargreaves = np.vectorize(calculate_solar_declination_hargreaves)(days)  # Calculate solar declination for each day

    fig = plt.figure(figsize=(10,6))
    plt.plot(days, solar_declinations, label='PVGIS')
    plt.plot(days, solar_declinations_hargreaves, label='Hargreaves')
    plt.xlabel('Day of the Year')
    plt.ylabel(f'Solar Declination in {year}')
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.savefig('solar_declination.png')
    return fig


def plot_solar_declination_five_years(
        start_year: int,
        end_year: int,
        title: str = 'Annual Variation of Solar Declination',
        ):
    days = [days_in_year(year) for year in np.arange(start_year, end_year)]
    solar_declinations = np.vectorize(calculate_solar_declination)(days, output_units='degrees')  # Calculate solar declination for each day
    solar_declinations_hargreaves = np.vectorize(calculate_solar_declination_hargreaves)(days)  # Calculate solar declination for each day

    fig = plt.figure(figsize=(10,6))
    plt.plot(days, solar_declinations, label='PVGIS')
    plt.plot(days, solar_declinations_hargreaves, label='Hargreaves')
    plt.xlabel('Day of the Year')
    plt.ylabel('Solar Declination')
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.savefig('solar_declination.png')
    return fig
