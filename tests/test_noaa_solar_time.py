import pytest
from pvgisprototype import Longitude
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.algorithms.noaa.solar_time import calculate_true_solar_time_time_series_noaa

test_cases_true_solar_time = [
    (
        Longitude(value=0.5, unit='radians'),
        [datetime(2023, 8, 25, 0, 0), datetime(2023, 8, 26, 0, 0)],
        ZoneInfo('UTC'),
        'minutes',
        'radians',
    ),
    # add more test cases
]

@pytest.mark.parametrize(
    "longitude, timestamps, timezone, time_output_units, angle_units",
    test_cases_true_solar_time,
)
def test_calculate_true_solar_time_time_series_noaa(
    longitude,
    timestamps,
    timezone,
    time_output_units,
    angle_units,
):
    calculated_true_solar_times = calculate_true_solar_time_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        time_output_units=time_output_units,
        angle_units=angle_units,
    )
    assert len(timestamps) == len(calculated_true_solar_times)
    assert all(isinstance(time, datetime) for time in calculated_true_solar_times)


def plot_true_solar_time_noaa(
    longitude,
    timestamps,
    timezone,
    time_output_units,
    angle_units,
    expected_true_solar_time_series,
):
    calculated_true_solar_time_series = calculate_true_solar_time_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        time_output_units=time_output_units,
        angle_units=angle_units,
    )
    figure, ax = plt.subplots()
    ax.plot(
        timestamps,
        [time.hour + time.minute/60 for time in expected_true_solar_time_series],
        label="Expected",
    )
    ax.plot(
        timestamps,
        [time.hour + time.minute/60 for time in calculated_true_solar_time_series],
        label="Calculated",
    )
    ax.set_xlabel("Timestamps")
    ax.set_ylabel("True Solar Time (hours)")
    ax.legend()
    plt.savefig(f'true_solar_time_series_noaa.png')
    return figure
