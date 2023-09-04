from pvgisprototype.api.irradiance.extraterrestrial import calculate_extraterrestrial_normal_irradiance
import matplotlib.pyplot as plt
import numpy as np
from pvgisprototype.api.utilities.timestamp import get_days_in_year
from pvgisprototype.api.utilities.timestamp import generate_timestamps_for_a_year


def plot_extraterrestrial_irradiance():
    days = np.arange(1, 366)  # Days in year -- use function to get real days in year
    extraterrestrial_irradiances = np.vectorize(calculate_extraterrestrial_normal_irradiance)(days)
    timestamps = generate_timestamps_for_a_year(year=year)

    fig = plt.figure(figsize=(10,6))
    plt.plot(days, extraterrestrial_irradiances, label='Solar Constant')

    # Average solar constant
    average_extraterrestrial_irradiance = 1360.8  # Make it an external constant?
    plt.axhline(y=average_extraterrestrial_irradiance, color='gray', linestyle='--', label='Average Solar Constant')

    # # Plot perigee
    # Perigee day : January 2 at 8:18pm or day number :
    perigee_day = 2.8408 
    perigee_value = calculate_extraterrestrial_normal_irradiance(perigee_day)
    plt.scatter(perigee_day, perigee_value, c='red', marker='o', label='Perigee')

    days_in_year = get_days_in_year(year)
    # Plot apogee
    perigee_offset = 0.048869
    apogee_day = 0.5 * (365.25 + perigee_offset)
    apogee_value = calculate_extraterrestrial_normal_irradiance(apogee_day)
    plt.scatter(apogee_day, apogee_value, c='blue', marker='o', label='Apogee')
    
    plt.xlabel('Day of the Year')
    plt.ylabel('Solar Constant (W/m^2)')
    plt.title('Annual Variation of Solar Constant')
    plt.grid(True)
    plt.legend(loc='lower right')
    plt.savefig('extraterrestrial_irradiance.png')
    return fig

plot_extraterrestrial_irradiance()
