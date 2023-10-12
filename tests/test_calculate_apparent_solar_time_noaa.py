import pytest
from datetime import datetime
# from pvgisprototype.algorithms.noaa.solar_time import calculate_true_solar_time_time_series_noaa
from pvgisprototype.algorithms.noaa.solar_time import calculate_apparent_solar_time_noaa
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import SOLAR_TIME_NAME
from pvgisprototype.api.utilities.timestamp import timestamp_to_minutes


test_cases_data = read_noaa_spreadsheet(
    './tests/data/test_cases_noaa_spreadsheet.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit='minutes',
    longitude='longitude',
    timestamp='timestamp',
    timezone='timezone',
    solar_time=SOLAR_TIME_NAME,
)

tolerances = [0.1]

@pytest.mark.parametrize(
    "longitude, timestamp, timezone, expected_solar_time, against_unit",
    test_cases,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_apparent_solar_time_noaa(
    longitude,
    timestamp,
    timezone,
    expected_solar_time,
    against_unit,
    tolerance,
):
    assert against_unit == expected_solar_time[1] == 'minutes'
    calculated_solar_time = calculate_apparent_solar_time_noaa(
        longitude=longitude,
        timestamp=timestamp,
        timezone=timezone,
    )

    calculated_solar_time_in_minutes = timestamp_to_minutes(calculated_solar_time)

    # Check types
    assert isinstance(calculated_solar_time, datetime)

    # Assert output
    assert pytest.approx(expected_solar_time[0], tolerance) == calculated_solar_time_in_minutes






# test_cases_true_solar_time = [
#     (
#         Longitude(value=0.5, unit='radians'),
#         [datetime(2023, 8, 25, 0, 0), datetime(2023, 8, 26, 0, 0)],
#         ZoneInfo('UTC'),
#         'minutes',
#         'radians',
#     ),
#     # add more test cases
# ]

# @pytest.mark.parametrize(
#     "longitude, timestamps, timezone, time_output_units, angle_units",
#     test_cases_true_solar_time,
# )
# def test_calculate_true_solar_time_time_series_noaa(
#     longitude,
#     timestamps,
#     timezone,
#     time_output_units,
#     angle_units,
# ):
#     calculated_true_solar_times = calculate_true_solar_time_time_series_noaa(
#         longitude=longitude,
#         timestamps=timestamps,
#         timezone=timezone,
#         time_output_units=time_output_units,
#         angle_units=angle_units,
#     )
#     assert len(timestamps) == len(calculated_true_solar_times)
#     assert all(isinstance(time, datetime) for time in calculated_true_solar_times)


# def plot_true_solar_time_noaa(
#     longitude,
#     timestamps,
#     timezone,
#     time_output_units,
#     angle_units,
#     expected_true_solar_time_series,
# ):
#     calculated_true_solar_time_series = calculate_true_solar_time_time_series_noaa(
#         longitude=longitude,
#         timestamps=timestamps,
#         timezone=timezone,
#         time_output_units=time_output_units,
#         angle_units=angle_units,
#     )
#     figure, ax = plt.subplots()
#     ax.plot(
#         timestamps,
#         [time.hour + time.minute/60 for time in expected_true_solar_time_series],
#         label="Expected",
#     )
#     ax.plot(
#         timestamps,
#         [time.hour + time.minute/60 for time in calculated_true_solar_time_series],
#         label="Calculated",
#     )
#     ax.set_xlabel("Timestamps")
#     ax.set_ylabel("True Solar Time (hours)")
#     ax.legend()
#     plt.savefig(f'true_solar_time_series_noaa.png')
#     return figure
