from devtools import debug
import pytest
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import time
from datetime import timedelta
from datetime import timezone
from zoneinfo import ZoneInfo
from math import radians

from pvgisprototype.api.geometry.solar_time import calculate_solar_time
from pvgisprototype.api.geometry.solar_hour_angle import calculate_hour_angle
from pvgisprototype import SolarHourAngle
from pvgisprototype.api.geometry.solar_hour_angle import calculate_hour_angle_sunrise

from pvgisprototype.algorithms.pyephem.solar_time import calculate_solar_time_ephem
from pvgisprototype.algorithms.milne1921.solar_time import calculate_apparent_solar_time_milne1921
from pvgisprototype.algorithms.pvgis.solar_geometry import calculate_solar_time_pvgis
from pvgisprototype.api.geometry.models import SolarTimeModels

from pvgisprototype.api.utilities.conversions import convert_to_radians
from pvgisprototype.api.utilities.timestamp import convert_hours_to_seconds
from pvgisprototype.api.utilities.timestamp import convert_to_timezone

from pvgisprototype.plot.plot_solar_time import plot_solar_time
from pvgisprototype.plot.plot_solar_time import plot_solar_time_one_year
from pvgisprototype.plot.plot_solar_time import plot_solar_time_one_year_bokeh
from pvgisprototype.plot.plot_solar_time import plot_solar_time_one_year_bokeh_static

import numpy as np
import random


# Set a seed to ensure agreement of plots between tests!
random.seed(43) # Comment to really pick a random year
random_year = random.randint(2005, 2023)


models = [
        SolarTimeModels.ephem,
        SolarTimeModels.milne,
        SolarTimeModels.noaa,
        SolarTimeModels.pvgis,
        SolarTimeModels.skyfield,
]
locations = [
    (0, 90, 'North Pole', 'UTC'),
    (0, -90, 'South Pole', 'UTC'),
    (-180, 0, 'International Date Line', 'UTC'),
    (0, 0, 'Greenwich Meridian/Equator', 'UTC'),
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
expected_solar_time = [
        (-3.1555168792302877),  # UPDATE-ME
        # (-3.1555168792302877),  # UPDATE-ME
]
@pytest.mark.parametrize("longitude, latitude", coordinates)
@pytest.mark.parametrize("timestamp", timestamps)
@pytest.mark.parametrize("timezone", timezones)
@pytest.mark.parametrize("model", models)
@pytest.mark.parametrize("expected_solar_time", expected_solar_time)
def test_calculate_solar_time(
        longitude,
        latitude,
        timestamp,
        timezone,
        model,
        expected_solar_time):
    longitude = radians(longitude)
    latitude = radians(latitude)
    timezone = ZoneInfo(timezone)
    result = calculate_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_time_models=[model],
    )
    debug(locals())
    assert result == pytest.approx(expected_solar_time)


@pytest.mark.parametrize("longitude, latitude, location, timezone", locations)
@pytest.mark.mpl_image_compare  # use a baseline image
def test_plot_solar_time(longitude, latitude, location, timezone):
    return plot_solar_time(
            longitude,
            latitude,
            location,
            timezone,
            [model],
            )


# @pytest.mark.parametrize("longitude, latitude, location, timezone", locations)
# @pytest.mark.parametrize("year", [random_year])
# @pytest.mark.parametrize("model", models)
# @pytest.mark.mpl_image_compare
# def test_plot_solar_time_one_year(
#         longitude,
#         latitude,
#         timezone,
#         year,
#         model,
#         location
# ):
#     return plot_solar_time_one_year(
#             longitude,
#             latitude,
#             timezone,
#             year,
#             [model],
#             location,
#             )


@pytest.mark.parametrize("longitude, latitude, location, timezone", locations)
@pytest.mark.parametrize("year", [random_year])
@pytest.mark.mpl_image_compare
def test_plot_solar_time_models_one_year(
        longitude,
        latitude,
        timezone,
        year,
        location
):
    return plot_solar_time_one_year(
            longitude,
            latitude,
            timezone,
            year,
            models,
            location,
            )


# @pytest.mark.parametrize("longitude, latitude, location, timezone", locations)
# @pytest.mark.parametrize("year", [random_year])
# @pytest.mark.parametrize("model", models)
# @pytest.mark.mpl_image_compare
# def test_plot_solar_time_model_one_year_bokeh_static(
#         longitude,
#         latitude,
#         timezone,
#         year,
#         model,
#         location
# ):
#     # debug(locals())
#     return plot_solar_time_one_year_bokeh_static(
#             longitude,
#             latitude,
#             timezone,
#             year,
#             [model],
#             location,
#             )


@pytest.mark.parametrize("longitude, latitude, location, timezone", locations)
@pytest.mark.parametrize("year", [random_year])
@pytest.mark.mpl_image_compare
def test_plot_solar_time_models_one_year_bokeh_static(
        longitude,
        latitude,
        timezone,
        year,
        location
):
    # debug(locals())
    return plot_solar_time_one_year_bokeh_static(
            longitude,
            latitude,
            timezone,
            year,
            models,
            location,
            )


@pytest.mark.parametrize("longitude, latitude, location, timezone", locations)
@pytest.mark.parametrize("year", [random_year])
@pytest.mark.parametrize("model", models)
@pytest.mark.mpl_image_compare
def test_plot_solar_time_one_year_bokeh(
        longitude,
        latitude,
        timezone,
        year,
        model,
        location
):
    # debug(locals())
    return plot_solar_time_one_year_bokeh(
            longitude,
            latitude,
            timezone,
            year,
            [model],
            location,
            )

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
    # ('degrees'),
]
tolerances = [
        # 0.00000000000000001,
        # 0.0000000000000001,
        # 0.000000000000001,
        # 0.00000000000001,
        # 0.0000000000001,
        # 0.000000000001,
        # 0.00000000001,
        # 0.0000000001,
        # 0.000000001,
        # 0.00000001,
        # 0.0000001,
        # 0.000001,
        # 0.00001,
        # 0.0001,
        0.001,
        # 0.01,
        0.1,
        ]
@pytest.mark.parametrize("solar_time, expected", cases)
@pytest.mark.parametrize("angle_output_units", units)
@pytest.mark.parametrize("tolerance", tolerances)
def test_calculate_hour_angle(solar_time, angle_output_units, expected, tolerance):
    # expected is a `time` object
    solar_time = time(hour=solar_time, minute=0, second=0) 
    calculated = calculate_hour_angle(solar_time)
    assert isinstance(calculated, SolarHourAngle)
    assert pytest.approx(expected, tolerance) == calculated.value
    assert angle_output_units == calculated.unit


@pytest.mark.mpl_image_compare
@pytest.mark.parametrize("angle_output_units", units)
def test_calculate_hour_angle_plot(angle_output_units):
    calculated_hour_angles = []
    expected_hour_angles = []
    for solar_time, expected_hour_angle in cases:
        # convert `solar_time` to seconds as expected
        solar_time_in_seconds = solar_time * 3600
        calculated_hour_angle = calculate_hour_angle(
            solar_time=solar_time_in_seconds,
        )
        calculated_hour_angles.append(calculated_hour_angle.value)
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
