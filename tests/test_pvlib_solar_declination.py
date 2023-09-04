import pytest
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
from pvgisprototype.algorithms.pvlib.solar_declination import calculate_solar_declination_pvlib
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarDeclination
import numpy as np
import matplotlib.pyplot as plt
from pvgisprototype.api.utilities.timestamp import random_datetimezone
from .cases_solar_declination import cases_for_solar_declination


tolerances = [
    1,
    0.5,
    0.1,
    0.01,
    0.001,
    0.0001,
]

@pytest.mark.parametrize(
    "timestamp, angle_output_units, expected",
    cases_for_solar_declination,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_declination_pvlib(
    timestamp,
    angle_output_units,
    expected,
    tolerance,
):
    """ """
    calculated = calculate_solar_declination_pvlib(
        timestamp=timestamp,
        angle_output_units=angle_output_units,
    )
    assert pytest.approx(expected, abs=tolerance) == calculated.value
    assert angle_output_units == calculated.unit
    assert (-0.4092797096 <= calculated.value <= 0.4092797096) or (-23.45 <= calculated.value <= 23.45)





def generate_timestamps_for_a_year(start_date=datetime(2023, 1, 1), frequency_minutes=60):
    timestamps = [start_date + timedelta(minutes=i * frequency_minutes) for i in range(365 * 24 * 60 // frequency_minutes)]
    return timestamps


def plot_solar_declination_pvlib(
    timestamps,
    angle_output_units,
    expected_solar_declination_series,
):
    calculated_solar_declination_series = [calculate_solar_declination_pvlib(
        timestamp,
        angle_output_units,
    ) for timestamp in timestamps]

    figure, ax = plt.subplots()
    ax.plot(
        timestamps,
        [declination.value for declination in expected_solar_declination_series],
        label="Expected",
    )
    ax.plot(
        timestamps,
        [declination.value for declination in calculated_solar_declination_series],
        label="Calculated",
    )
    ax.set_xlabel("Timestamps")
    ax.set_ylabel(f"Solar Declination ({angle_output_units})")
    ax.legend()
    plt.savefig(f'solar_declination_series_pvlib.png')
    return figure



def get_expected_solar_declinations(timestamps, longitude, latitude):
    # Here, you can use a reference model or data to get the expected solar declinations
    # For demonstration purposes, I'm returning an array of SolarDeclination objects with dummy values
    return [SolarDeclination(value=0.2, unit='radians') for _ in timestamps]




timestamps_for_a_year = generate_timestamps_for_a_year()
longitude = Longitude(value=0.5585053606381855, unit='radians')
latitude = Latitude(value=0.47123889803846897, unit='radians')
angle_output_units = 'degrees'


@pytest.mark.mpl_image_compare
def test_plot_solar_declination_pvlib():
    expected_solar_declination_series = get_expected_solar_declinations(timestamps_for_a_year, longitude, latitude)
    return plot_solar_declination_pvlib(
        timestamps_for_a_year,
        angle_output_units,
        expected_solar_declination_series,
    )
