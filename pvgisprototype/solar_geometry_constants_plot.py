import matplotlib.pyplot as plt
import numpy as np
from pvgisprototype.data_structures import SolarGeometryDayConstants
from pvgisprototype.solar_geometry_constants import calculate_solar_geometry_constants
from pvgisprototype.solar_declination import calculate_solar_declination


def plot_sunrise_sunset(latitude: float, start_day: int, end_day: int):
    """
    Plot the sunrise and sunset times over a range of days.

    Parameters
    ----------
    grid_geometry : GridGeometry
        Grid geometry constants.
    start_day : int
        Start day for the plot.
    end_day : int
        End day for the plot.

    """
    days = np.arange(start_day, end_day+1)
    sunrise_times = []
    sunset_times = []

    for day in days:
        solar_declination = calculate_solar_declination(day)
        # convert to radians maybe? : np.radians(solar_declination)
        solar_geometry_day_constants = calculate_solar_geometry_constants(
                latitude=latitude,
                local_solar_time=12,  # Assuming local solar time as noon
                solar_declination=solar_declination,
                time_offset=0.0  # Assuming time offset as 0
                )
        sunrise_times.append(solar_geometry_day_constants.sunrise_time)
        sunset_times.append(solar_geometry_day_constants.sunset_time)

    fig = plt.figure(figsize=(10, 5))
    plt.plot(days, sunrise_times, label='Sunrise')
    plt.plot(days, sunset_times, label='Sunset')
    plt.xlabel('Day')
    plt.ylabel('Time (hours)')
    plt.title(f'Sunrise and Sunset Times @ {latitude} degrees latitude')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'solar_geometry_day_constants_at_{latitude}_latitude.png')
    return fig
