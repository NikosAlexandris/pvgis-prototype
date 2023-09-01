import pytest
from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo
from pvgisprototype.algorithms.noaa.solar_azimuth import calculate_solar_azimuth_time_series_noaa
from pvgisprototype import Longitude, Latitude, SolarAzimuth
import numpy as np
import matplotlib.pyplot as plt


test_cases_azimuth = [
    (
        Longitude(value=0.5, unit='radians'),
        Latitude(value=0.5, unit='radians'),
        [datetime(2023, 8, 25, 0, 0), datetime(2023, 8, 26, 0, 0)],
        ZoneInfo('UTC'),
        False,
        'minutes',
        'radians',
        'radians',
    ),
    # add more test cases
]


@pytest.mark.parametrize(
    'longitude, latitude, timestamps, timezone, apply_atmospheric_refraction, time_output_units, angle_units, angle_output_units',
    test_cases_azimuth,
)
def test_calculate_solar_azimuth_time_series_noaa(
    longitude,
    latitude,
    timestamps,
    timezone,
    apply_atmospheric_refraction,
    time_output_units,
    angle_units,
    angle_output_units,
):
    calculated_azimuth_series = calculate_solar_azimuth_time_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    assert np.ndarray == type(calculated_azimuth_series)
    assert len(timestamps) == len(calculated_azimuth_series)
    assert all(SolarAzimuth == type(azimuth) for azimuth in calculated_azimuth_series)
    assert all((0 <= azimuth.value <= 2*np.pi) for azimuth in calculated_azimuth_series)
    assert all(angle_output_units == azimuth.unit for azimuth in calculated_azimuth_series)


def plot_solar_azimuth_noaa(
    longitude,
    latitude,
    timestamps,
    timezone,
    apply_atmospheric_refraction,
    time_output_units,
    angle_units,
    angle_output_units,
    expected_solar_azimuth_series,
):
    calculated_solar_azimuth_series = calculate_solar_azimuth_time_series_noaa(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
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
    plt.savefig(f'solar_azimuth_series_noaa.png')
    return figure
