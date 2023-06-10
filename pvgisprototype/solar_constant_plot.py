from pvgisprototype.solar_constant import calculate_solar_constant
import matplotlib.pyplot as plt
import numpy as np


def plot_solar_constant():
    days = np.arange(1, 366)  # Days of the year
    solar_constants = np.vectorize(calculate_solar_constant)(days)  # Calculate solar constant for each day

    fig = plt.figure(figsize=(10,6))
    plt.plot(days, solar_constants)
    plt.xlabel('Day of the Year')
    plt.ylabel('Solar Constant (W/m^2)')
    plt.title('Annual Variation of Solar Constant')
    plt.grid(True)
    plt.savefig('solar_constant.png')
    return fig

plot_solar_constant()
