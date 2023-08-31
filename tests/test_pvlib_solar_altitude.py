import pytest
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
from pvgisprototype.models.pvlib.solar_altitude import calculate_solar_altitude_pvlib
from pvgisprototype.api.data_classes.models import Longitude
from pvgisprototype.api.data_classes.models import Latitude
from pvgisprototype.api.data_classes.models import SolarAltitude
import numpy as np
import matplotlib.pyplot as plt
from pvgisprototype.api.utilities.timestamp import random_datetimezone


def generate_timestamps_for_a_year(start_date=datetime(2023, 1, 1), frequency_minutes=60):
    timestamps = [start_date + timedelta(minutes=i * frequency_minutes) for i in range(365 * 24 * 60 // frequency_minutes)]
    return timestamps


longitude = Longitude(value=0.1, unit='radians')
latitude = Latitude(value=0.1, unit='radians')
timestamps_for_a_year = generate_timestamps_for_a_year()
timezone = ZoneInfo('UTC')
# apply_atmospheric_refraction = False
# time_output_units = 'minutes'
angle_output_units = 'radians'


test_cases = [
    (
        Longitude(value=0.5, unit='radians'),
        Latitude(value=0.5, unit='radians'),
        [datetime(2023, 8, 25, 0, 0), datetime(2023, 8, 26, 0, 0)],
        ZoneInfo('UTC'),
        'radians',
    ),
    # TODO: Add more test cases here
]


@pytest.mark.parametrize(
    "longitude, latitude, timestamps, timezone, angle_output_units",
    test_cases,
)
def test_calculate_solar_altitude_pvlib(
    longitude,
    latitude,
    timestamps,
    timezone,
    angle_output_units,
):
    """ """
    calculated_altitude_series = calculate_solar_altitude_pvlib(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamps,
        timezone=timezone,
        angle_output_units=angle_output_units,
    )
    # assert np.ndarray == type(calculated_altitude_series)
    assert len(timestamps) == len(calculated_altitude_series)
    assert all(SolarAltitude == type(altitude) for altitude in calculated_altitude_series)
    assert all((-np.pi/2 <= altitude.value <= np.pi/2) for altitude in calculated_altitude_series)
    assert all(angle_output_units == altitude.unit for altitude in calculated_altitude_series)




def plot_solar_altitude_pvlib(
    longitude,
    latitude,
    timestamps,
    timezone,
    angle_output_units,
    expected_solar_altitude_series,
):
    calculated_solar_altitude_series = calculate_solar_altitude_pvlib(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        angle_output_units=angle_output_units,
    )
    figure, ax = plt.subplots()
    ax.plot(
        timestamps,
        [altitude.value for altitude in expected_solar_altitude_series],
        label="Expected",
    )
    ax.plot(
        timestamps,
        [altitude.value for altitude in calculated_solar_altitude_series],
        label="Calculated",
    )
    ax.set_xlabel("Timestamps")
    ax.set_ylabel(f"Solar Altitude ({angle_output_units})")
    ax.legend()
    plt.savefig(f'solar_altitude_series_pvlib.png')
    return figure



def get_expected_solar_altitudes(timestamps, longitude, latitude):
    # Here, you can use a reference model or data to get the expected solar altitudes
    # For demonstration purposes, I'm returning an array of SolarAltitude objects with dummy values
    return [SolarAltitude(value=0.5, unit='radians') for _ in timestamps]


@pytest.mark.mpl_image_compare
def test_plot_solar_altitude_pvlib():
    expected_solar_altitude_series = get_expected_solar_altitudes(timestamps_for_a_year, longitude, latitude)
    return plot_solar_altitude_pvlib(
        longitude,
        latitude,
        timestamps_for_a_year,
        timezone,
        angle_output_units,
        expected_solar_altitude_series,
    )
