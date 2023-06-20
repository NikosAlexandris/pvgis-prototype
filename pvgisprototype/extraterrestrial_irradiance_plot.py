from pvgisprototype.solar_constant import calculate_solar_constant
import matplotlib.pyplot as plt
import numpy as np


def plot_solar_constant():
    days = np.arange(1, 366)  # Days of the year
    solar_constants = np.vectorize(calculate_solar_constant)(days)  # Calculate solar constant for each day

    fig = plt.figure(figsize=(10,6))
    plt.plot(days, solar_constants, label='Solar Constant')

    # Average solar constant
    average_solar_constant = 1367
    plt.axhline(y=average_solar_constant, color='gray', linestyle='--', label='Average Solar Constant')

    # # Plot perigee
    # Perigee day : January 2 at 8:18pm or day number :
    perigee_day = 2.8408 
    perigee_value = calculate_solar_constant(perigee_day)
    plt.scatter(perigee_day, perigee_value, c='red', marker='o', label='Perigee')

    # Plot apogee
    perigee_offset = 0.048869
    apogee_day = 0.5 * (365.25 + perigee_offset)
    apogee_value = calculate_solar_constant(apogee_day)
    plt.scatter(apogee_day, apogee_value, c='blue', marker='o', label='Apogee')
    
    plt.xlabel('Day of the Year')
    plt.ylabel('Solar Constant (W/m^2)')
    plt.title('Annual Variation of Solar Constant')
    plt.grid(True)
    plt.legend(loc='lower right')
    plt.savefig('solar_constant.png')
    return fig

plot_solar_constant()
