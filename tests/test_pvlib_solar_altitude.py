import pytest
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
from pvgisprototype.algorithms.pvlib.solar_altitude import calculate_solar_altitude_pvlib
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarAltitude
import numpy as np
import matplotlib.pyplot as plt
from pvgisprototype.api.utilities.timestamp import random_datetimezone
from .cases_solar_altitude import cases_for_solar_altitude


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
    cases_for_solar_altitude,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_altitude_pvlib(
    longitude,
    latitude,
    timestamp,
    timezone,
    angle_output_units,
    expected,
    tolerance,
):
    """ """
    calculated = calculate_solar_altitude_pvlib(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        angle_output_units=angle_output_units,
    )
    assert pytest.approx(expected, abs=tolerance) == calculated.value
    assert angle_output_units == calculated.unit
    assert (-np.pi/2 <= calculated.value <= np.pi/2) or (-90 <= calculated.value <= 90)





def generate_timestamps_for_a_year(start_date=datetime(2023, 1, 1), frequency_minutes=60):
    timestamps = [start_date + timedelta(minutes=i * frequency_minutes) for i in range(365 * 24 * 60 // frequency_minutes)]
    return timestamps


def plot_solar_altitude_pvlib(
    longitude,
    latitude,
    timestamps,
    timezone,
    angle_output_units,
    expected_solar_altitude_series,
):
    calculated_solar_altitude_series = [calculate_solar_altitude_pvlib(
        longitude,
        latitude,
        timestamp,
        timezone,
        angle_output_units,
    ) for timestamp in timestamps]

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




timestamps_for_a_year = generate_timestamps_for_a_year()
longitude = Longitude(value=0.5585053606381855, unit='radians')
latitude = Latitude(value=0.47123889803846897, unit='radians')
# timestamp = datetime(2024, 9, 4, 7, 32)
timezone = ZoneInfo('UTC')
angle_output_units = 'degrees'


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
