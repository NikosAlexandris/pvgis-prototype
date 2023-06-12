from pvgisprototype.solar_declination import calculate_solar_declination
from pvgisprototype.solar_declination import calculate_solar_declination_hargreaves
import matplotlib.pyplot as plt
import numpy as np


def plot_solar_declination():
    days = np.arange(1, 366)  # Days of the year
    solar_declinations = np.vectorize(calculate_solar_declination)(days, output_units='degrees')  # Calculate solar declination for each day
    solar_declinations_hargreaves = np.vectorize(calculate_solar_declination_hargreaves)(days)  # Calculate solar declination for each day

    fig = plt.figure(figsize=(10,6))
    plt.plot(days, solar_declinations, label='PVGIS')
    plt.plot(days, solar_declinations_hargreaves, label='Hargreaves')
    plt.xlabel('Day of the Year')
    plt.ylabel('Solar Declination')
    plt.title('Annual Variation of Solar Declination')
    plt.grid(True)
    plt.legend()
    plt.savefig('solar_declination.png')
    return fig

plot_solar_declination()
