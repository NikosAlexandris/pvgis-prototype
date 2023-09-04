import pytest
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
from pvgisprototype.algorithms.pvlib.solar_azimuth import calculate_solar_azimuth_pvlib
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarAzimuth
import numpy as np
import matplotlib.pyplot as plt
from pvgisprototype.api.utilities.timestamp import random_datetimezone
from .cases_solar_azimuth import cases_for_solar_azimuth


tolerances = [
    1,
    0.5,
    0.1,
    # 0.01,
    # 0.001,
    # 0.0001,
]

@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone, angle_output_units, expected",
    cases_for_solar_azimuth,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_azimuth_pvlib(
    longitude,
    latitude,
    timestamp,
    timezone,
    angle_output_units,
    expected,
    tolerance,
):
    """ """
    calculated = calculate_solar_azimuth_pvlib(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        angle_output_units=angle_output_units,
    )
    assert pytest.approx(expected, abs=tolerance) == calculated.value
    assert angle_output_units == calculated.unit
    assert (0 <= calculated.value <= 2*np.pi) or (0 <= calculated.value <= 360)





def generate_timestamps_for_a_year(start_date=datetime(2023, 1, 1), frequency_minutes=60):
    timestamps = [start_date + timedelta(minutes=i * frequency_minutes) for i in range(365 * 24 * 60 // frequency_minutes)]
    return timestamps


def plot_solar_azimuth_pvlib(
    longitude,
    latitude,
    timestamps,
    timezone,
    angle_output_units,
    expected_solar_azimuth_series,
):
    calculated_solar_azimuth_series = [calculate_solar_azimuth_pvlib(
        longitude,
        latitude,
        timestamp,
        timezone,
        angle_output_units,
    ) for timestamp in timestamps]

    figure, ax = plt.subplots()
    ax.plot(
        timestamps,
        [azimuth.value for azimuth in expected_solar_azimuth_series],
        label="Expected",
    )
    ax.plot(
        timestamps,
        [azimuth.value for azimuth in calculated_solar_azimuth_series],
        label="Calculated",
    )
    ax.set_xlabel("Timestamps")
    ax.set_ylabel(f"Solar Azimuth ({angle_output_units})")
    ax.legend()
    plt.savefig(f'solar_azimuth_series_pvlib.png')
    return figure



def get_expected_solar_azimuths(timestamps, longitude, latitude):
    # Here, you can use a reference model or data to get the expected solar azimuths
    # For demonstration purposes, I'm returning an array of SolarAzimuth objects with dummy values
    return [SolarAzimuth(value=0.5, unit='radians') for _ in timestamps]




timestamps_for_a_year = generate_timestamps_for_a_year()
longitude = Longitude(value=0.5585053606381855, unit='radians')
latitude = Latitude(value=0.47123889803846897, unit='radians')
# timestamp = datetime(2024, 9, 4, 7, 32)
timezone = ZoneInfo('UTC')
angle_output_units = 'degrees'


@pytest.mark.mpl_image_compare
def test_plot_solar_azimuth_pvlib():
    expected_solar_azimuth_series = get_expected_solar_azimuths(timestamps_for_a_year, longitude, latitude)
    return plot_solar_azimuth_pvlib(
        longitude,
        latitude,
        timestamps_for_a_year,
        timezone,
        angle_output_units,
        expected_solar_azimuth_series,
    )
