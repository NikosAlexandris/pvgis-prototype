from devtools import debug
import pytest
from datetime import datetime
from datetime import timedelta
from math import pi, isclose
from pvgisprototype.models.noaa.fractional_year import calculate_fractional_year_noaa
from pvgisprototype.models.noaa.fractional_year import calculate_fractional_year_time_series_noaa
from pvgisprototype.models.noaa.fractional_year import FractionalYear
import pydantic
import numpy as np


test_cases = [
    (datetime(year=2023, month=7, day=25, hour=12), 3.55),  # specific date
    (datetime(year=2023, month=1, day=1, hour=0), 0),  # boundary case of 0
    (datetime(year=2023, month=12, day=31, hour=23), 2*pi),  # boundary case of 2*pi
]
tolerances = [1, 0.1]


@pytest.fixture
def timestamps_for_a_year():
    start_date = datetime(year=2023, month=1, day=1, hour=0)
    return [start_date + timedelta(hours=i) for i in range(365 * 24)]


@pytest.fixture
def expected_fractional_years_for_a_year(timestamps_for_a_year):
    return [calculate_fractional_year_noaa(timestamp).value for timestamp in timestamps_for_a_year]


@pytest.mark.parametrize("timestamp, expected_fractional_year", test_cases)
def test_calculate_fractional_year_noaa(timestamp, expected_fractional_year):
    fractional_year = calculate_fractional_year_noaa(timestamp)
    assert 'radians' == fractional_year.unit
    assert isclose(expected_fractional_year, fractional_year.value, rel_tol=1e-2), "Fractional year calculation incorrect"


def test_calculate_fractional_year_noaa_invalid_input():
    # test an incorrect type of input
    with pytest.raises(pydantic.ValidationError):
        calculate_fractional_year_noaa("not a datetime object")

    # test an incorrect value of angle_output_units
    with pytest.raises(pydantic.ValidationError):
        calculate_fractional_year_noaa(datetime(year=2023, month=7, day=25, hour=12), angle_output_units="not a valid unit")


@pytest.mark.parametrize("timestamp, expected_fractional_year", test_cases)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_fractional_year_time_series_noaa_single_timestamp(timestamp, expected_fractional_year, tolerance):
    calculated = calculate_fractional_year_time_series_noaa(timestamp)
    assert isinstance(calculated[0], FractionalYear)
    assert pytest.approx(expected_fractional_year, abs=tolerance) == calculated[0].value
    assert 'radians' == calculated[0].unit


@pytest.fixture
def timestamps():
    return [
        datetime(2022, 3, 20, 12),
        datetime(2022, 6, 21, 12),
        datetime(year=2023, month=7, day=25, hour=12),
        datetime(year=2023, month=1, day=1, hour=0),
        datetime(year=2023, month=12, day=31, hour=23),
    ]


@pytest.fixture
def expected_fractional_years():
    return [
        1.34,
        2.94,
        3.55,
        0,
        2*pi,
    ]


@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_fractional_year_time_series_noaa(
    timestamps,
    expected_fractional_years,
    tolerance,
):
    calculated = calculate_fractional_year_time_series_noaa(timestamps)
    assert isinstance(calculated, np.ndarray)
    assert all(isinstance(item, FractionalYear) for item in calculated)
    assert np.allclose([item.value for item in calculated], expected_fractional_years, atol=tolerance)
    assert all(item.unit == 'radians' for item in calculated)


import matplotlib.pyplot as plt
import numpy as np


def plot_fractional_year_noaa(timestamps, expected, calculated):
    figure, ax = plt.subplots()
    calculated_values = [item.value for item in calculated]
    ax.plot(timestamps, expected, label="Expected")
    ax.plot(timestamps, calculated_values, label="Calculated")
    ax.set_xlabel("Timestamps")
    ax.set_ylabel("Fractional Year")
    ax.legend()
    plt.savefig(f'fractional_year_noaa.png')
    return figure


@pytest.mark.mpl_image_compare
def test_plot_fractional_year_noaa(timestamps, expected_fractional_years):
# def test_plot_fractional_year_noaa():
    calculated_fractional_years = calculate_fractional_year_time_series_noaa(timestamps)
    assert plot_fractional_year_noaa(
            timestamps,
            expected_fractional_years,
            calculated_fractional_years,
        )


@pytest.mark.mpl_image_compare
def test_plot_fractional_year_noaa(timestamps_for_a_year, expected_fractional_years_for_a_year):
# def test_plot_fractional_year_noaa():
    calculated_fractional_years_for_a_year = calculate_fractional_year_time_series_noaa(timestamps_for_a_year)
    assert plot_fractional_year_noaa(
            timestamps_for_a_year,
            expected_fractional_years_for_a_year,
            calculated_fractional_years_for_a_year,
        )
