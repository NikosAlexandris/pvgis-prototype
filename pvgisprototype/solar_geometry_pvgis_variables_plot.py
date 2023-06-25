import random
import matplotlib.pyplot as plt
import numpy as np
from pvgisprototype.data_structures import SolarGeometryDayConstants
from pvgisprototype.solar_geometry_pvgis_constants import calculate_solar_geometry_pvgis_constants
from pvgisprototype.solar_declination import calculate_solar_declination
from pvgisprototype.solar_geometry_pvgis_variables import calculate_solar_geometry_pvgis_variables
import datetime


# Set a seed to ensure agreement of plots between tests!
random.seed(43) # Comment to really pick a random year
year = random.randint(2005, 2020)


def plot_solar_geometry_pvgis_variables(longitude:float, latitude: float, start_date: datetime.datetime, end_date: datetime.datetime):
    """
    Plot the solar geometry variables over a range of days.

    Parameters
    ----------
    latitude : float
        The latitude of the location.

    start_date : datetime
        Start day for the plot.
    
    end_date : datetime
        End day for the plot.
    """
    solar_altitude_values = []
    solar_azimuth_values = []
    sun_azimuth_angle_values = []
    timestamps = [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days)]
    for timestamp in timestamps:
        solar_declination = calculate_solar_declination(timestamp)
        solar_geometry_day_constants = calculate_solar_geometry_pvgis_constants(
            longitude=longitude,
            latitude=latitude,
            local_solar_time=12,  # Assuming local solar time as noon
            solar_declination=solar_declination,
            time_offset=0.0  # Assuming time offset as 0
        )
        solar_geometry_day_variables = calculate_solar_geometry_pvgis_variables(
                solar_geometry_day_constants=solar_geometry_day_constants,
                timestamp=timestamp,
                output_units='degrees'
        )
        solar_altitude_values.append(solar_geometry_day_variables.solar_altitude)
        solar_azimuth_values.append(solar_geometry_day_variables.solar_azimuth)
        sun_azimuth_angle_values.append(solar_geometry_day_variables.sun_azimuth_angle)

    fig, axs = plt.subplots(3, figsize=(10, 15))
    axs[0].plot(timestamps, solar_altitude_values, label='Solar Altitude')
    axs[1].plot(timestamps, solar_azimuth_values, label='Solar Azimuth')
    axs[2].plot(timestamps, sun_azimuth_angle_values, label='Sun Azimuth Angle')

    for ax in axs:
        ax.set(xlabel='Day', ylabel='Angle (rad)')
        ax.legend()
        ax.grid(True)

    plt.suptitle(f'Solar geometry variables @ {latitude} degrees latitude')
    plt.tight_layout()
    plt.savefig('solar_geometry_day_variables.png')
    return fig
