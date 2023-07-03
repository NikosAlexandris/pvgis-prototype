import pytest
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import pytz
from pvgisprototype.api.geometry.solar_time import (
    calculate_solar_time_ephem,
    calculate_solar_time_eot,
    calculate_solar_time_pvgis,
    calculate_solar_time,
    calculate_hour_angle,
    calculate_hour_angle_sunrise,
    SolarTimeModels
)
from pvgisprototype.api.utilities.timestamp import convert_hours_to_seconds
from pvgisprototype.api.utilities.timestamp import convert_to_timezone
from pvgisprototype.plot.plot_solar_time import plot_solar_time
import numpy as np


# import typer
# from typer.testing import CliRunner
# app = typer.Typer()
# app.command()(calculate_hour_angle)
# runner = CliRunner()


@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone, expected_solar_time",
    [
        (0, 0, datetime(2023, 1, 1), 'UTC', -3.1555168792302877),  # UPDATE-ME
        (0, 0, datetime(2023, 1, 1), 'Europe/Athens', -3.1555168792302877),  # UPDATE-ME
    ]
)
def test_calculate_solar_time_ephem_simple(
        longitude,
        latitude,
        timestamp,
        timezone,
        expected_solar_time):
    result = calculate_solar_time_ephem(longitude, latitude, timestamp, timezone)
    assert result == pytest.approx(expected_solar_time)


models = [
        SolarTimeModels.ephem,
        SolarTimeModels.eot,
        SolarTimeModels.noaa,
        SolarTimeModels.pvgis,
        SolarTimeModels.skyfield,
]
coordinates = [
    (0, 90),  # 'North Pole'
    (0, -90),  # 'South Pole'
    (-180, 0), # 'International Date Line'
    (0, 0),  # 'Greenwich Meridian'
    (0, 0),  # 'Equator'
]
timestamps = [
    (datetime(2023, 6, 21)),  # 'Summer Solstice'
    (datetime(2023, 12, 21)),  # 'Winter Solstice'
    (datetime(2023, 3, 20)),  # 'March Equinox'
    (datetime(2023, 9, 22)),  # 'September Equinox'
    (datetime(2023, 1, 1, 6, 0)),  # 'Early Morning'
    (datetime(2023, 1, 1, 12, 0)),  # 'Midday'
    (datetime(2023, 1, 1, 18, 0)),  # 'Evening'
]
timezones = [
    ('UTC'),
    # ('America/New_York'),
    # ('Asia/Tokyo'),
    ('Europe/Athens'),
]
expected = [
        (-3.1555168792302877),  # UPDATE-ME
        # (-3.1555168792302877),  # UPDATE-ME
]
@pytest.mark.parametrize("longitude, latitude", coordinates)
@pytest.mark.parametrize("timestamp", timestamps)
@pytest.mark.parametrize("timezone", timezones)
@pytest.mark.parametrize("model", models)
@pytest.mark.parametrize("expected_solar_time", expected)
def test_calculate_solar_time(
        longitude,
        latitude,
        timestamp,
        timezone,
        model,
        expected_solar_time):
    result = calculate_solar_time(longitude, latitude, timestamp, timezone, model)
    assert result == pytest.approx(expected_solar_time)


# the list of models you want to test
models = [SolarTimeModels.ephem, SolarTimeModels.eot, SolarTimeModels.pvgis]


locations = [
    (0, 90, 'North Pole', 'UTC'),
    (0, -90, 'South Pole', 'UTC'),
    (-180, 0, 'International Date Line', 'UTC'),
    (0, 0, 'Greenwich Meridian / Equator', 'UTC'),
    (22.358611, 40.085556, 'Όλυμπος', 'Europe/Athens'),
    (6.6327, 46.5218, 'Lausanne, Switzerland', 'Europe/Zurich'),
    (-74.0060, 40.7128, 'New York, USA', 'America/New_York'),
    (-0.1278, 51.5074, 'London, UK', 'Europe/London'),
    (151.2093, -33.8688, 'Sydney, Australia', 'Australia/Sydney'),
    (139.6917, 35.6895, 'Tokyo, Japan', 'Asia/Tokyo'),
    (18.4241, -33.9249, 'Cape Town, South Africa', 'Africa/Johannesburg'),
    (-58.3816, -34.6037, 'Buenos Aires, Argentina', 'America/Argentina/Buenos_Aires'),
    (37.6176, 55.7558, 'Moscow, Russia', 'Europe/Moscow'),
    (103.8198, 1.3521, 'Singapore', 'Asia/Singapore'),
    (-21.8174, 64.1265, 'Reykjavik, Iceland', 'Atlantic/Reykjavik'),
    (-157.8583, 21.3069, 'Honolulu, Hawaii, USA', 'Pacific/Honolulu'),
    (72.8777, 19.0760, 'Mumbai (Bombay), India', 'Asia/Kolkata'),
]
@pytest.mark.parametrize("longitude, latitude, location, timezone", locations)
@pytest.mark.mpl_image_compare  # instructs use of a baseline image
def test_plot_solar_time(longitude, latitude, location, timezone):
    return plot_solar_time(
            longitude,
            latitude,
            location,
            timezone,
            [model],
            )



# @pytest.mark.parametrize("longitude, latitude", coordinates)
# @pytest.mark.parametrize("timestamp", timestamps)
# @pytest.mark.parametrize("timezone", timezones)
# @pytest.mark.parametrize("expexted_solar_time", expected)
# def test_calculate_solar_time_eot(
#         longitude,
#         latitude,
#         timestamp,
#         timezone,
#         expexted_solar_time):
#     result = calculate_solar_time_eot(longitude, latitude, timestamp, timezone)
#     assert result == pytest.approx(expexted_solar_time)


# @pytest.mark.parametrize("longitude, latitude", coordinates)
# @pytest.mark.parametrize("timestamp", timestamps)
# @pytest.mark.parametrize("timezone", timezones)
# @pytest.mark.parametrize("expexted_solar_time", expected)
# def test_calculate_solar_time_pvgis(
#         longitude,
#         latitude,
#         timestamp,
#         timezone,
#         expexted_solar_time):
#     result = calculate_solar_time_pvgis(longitude, latitude, timestamp, timezone)
#     assert result == pytest.approx(expexted_solar_time)

cases = [
    ( 1, -2.8875),
    ( 2, -2.625),
    ( 3, -2.3625),
    ( 4, -2.1),
    ( 5, -1.8375),
    ( 6, -1.575),
    ( 7, -1.3125),
    ( 8, -1.05),
    ( 9, -0.7875),
    (10, -0.525),
    (11, -0.2625),
    (12,  0),
    (13,  0.2625),
    (14,  0.525),
    (15,  0.7875),
    (16,  1.05),
    (17,  1.3125),
    (18,  1.575),
    (19,  1.8375),
    (20,  2.1),
    (21,  2.3625),
    (22,  2.625),
    (23,  2.8875),
]
units = [
    ('radians'),
    ('degrees'),
]
@pytest.mark.parametrize("solar_time, expected_hour_angle", cases)
def test_calculate_hour_angle(solar_time, expected_hour_angle):
    # Since we are not calling `calculate_hour_angle` through the command line,
    # the callback function `convert_hours_to_seconds` won't run!
    # Let's do this here:
    solar_time_in_seconds = convert_hours_to_seconds(solar_time)
    calculated_hour_angle = calculate_hour_angle(solar_time_in_seconds)
    assert calculated_hour_angle == pytest.approx(expected_hour_angle, 0.00000000000000001)


import matplotlib.pyplot as plt
@pytest.mark.mpl_image_compare  # instructs use of a baseline image
def test_calculate_hour_angle_plot():
    calculated_hour_angles = []
    expected_hour_angles = []
    for solar_time, expected_hour_angle in cases:
        # convert `solar_time` to seconds as expected
        solar_time_in_seconds = solar_time * 3600
        calculated_hour_angle = calculate_hour_angle(solar_time_in_seconds)
        calculated_hour_angles.append(calculated_hour_angle)
        expected_hour_angles.append(expected_hour_angle)

    fig = plt.figure(figsize=(10,6))
    plt.scatter(calculated_hour_angles, expected_hour_angles)
    # plt.plot(solar_time, calculated_hour_angle, label='calculated_hour_angle')
    # plt.plot(solar_time, expected_hour_angle, label='expected_hour_angle')
    # plt.xlabel('Solar Time (hours)')
    # plt.ylabel('Hour Angle (radians)')
    # plt.legend()
    plt.title('Calculated vs Expected Hour Angles')
    plt.savefig('hour_angle_from_solat_time_calculated_vs_expected.png')
    return fig


def test_calculate_hour_angle_sunrise():
    pass
