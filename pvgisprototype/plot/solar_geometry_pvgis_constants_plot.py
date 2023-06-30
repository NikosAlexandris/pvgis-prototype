import matplotlib.pyplot as plt
import numpy as np
from pvgisprototype.data_structures import SolarGeometryDayConstants
from pvgisprototype.solar_geometry_pvgis_constants import calculate_solar_geometry_pvgis_constants
from pvgisprototype.solar_declination import calculate_solar_declination
import datetime


def plot_sunrise_sunset(longitude: float, latitude: float, start_date: datetime.datetime, end_date: datetime.datetime):
    """
    Plot the sunrise and sunset times over a range of days.

    Parameters
    ----------
    grid_geometry : GridGeometry
        Grid geometry constants.
    start_date : datetime
        Start day for the plot.
    end_date : datetime
        End day for the plot.

    """
    sunrise_times = []
    sunset_times = []
    timestamps = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days)]
    for timestamp in timestamps:
        solar_declination = calculate_solar_declination(timestamp)
        # convert to radians maybe? : np.radians(solar_declination)
        solar_geometry_day_constants = calculate_solar_geometry_pvgis_constants(
                longitude=longitude,
                latitude=latitude,
                local_solar_time=12,  # Assuming local solar time as noon
                solar_declination=solar_declination,
                time_offset=0.0  # Assuming time offset as 0
                )
        sunrise_times.append(solar_geometry_day_constants.sunrise_time)
        sunset_times.append(solar_geometry_day_constants.sunset_time)

    fig = plt.figure(figsize=(10, 5))
    plt.plot(timestamps, sunrise_times, label='Sunrise')
    plt.plot(timestamps, sunset_times, label='Sunset')
    plt.xlabel('Day')
    plt.ylabel('Time (hours)')
    plt.title(f'Sunrise and Sunset Times @ {longitude}, {latitude} degrees')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'solar_sun_rise_set_at_longitude_{longitude}_latitude_{latitude}.png')
    return fig
