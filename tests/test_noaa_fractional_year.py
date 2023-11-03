from devtools import debug
import pytest
from datetime import datetime
from datetime import timedelta
from math import pi, isclose
from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_noaa
from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_time_series_noaa
from pvgisprototype.algorithms.noaa.fractional_year import FractionalYear
import pydantic
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from .cases.fractional_year import tolerances
from .cases.fractional_year import cases_for_fractional_year
from .cases.fractional_year import cases_for_fractional_year_series_single_timestamp
from .cases.fractional_year import timestamps
from .cases.fractional_year import cases_for_fractional_year_series
from pvgisprototype.constants import RADIANS


@pytest.mark.parametrize("timestamp, expected_fractional_year", cases_for_fractional_year)
def test_calculate_fractional_year_noaa(timestamp, expected_fractional_year):
    fractional_year = calculate_fractional_year_noaa(timestamp)
    assert RADIANS == fractional_year.unit
    assert isclose(expected_fractional_year, fractional_year.value, rel_tol=1e-2), "Fractional year calculation incorrect"


def test_calculate_fractional_year_noaa_invalid_input():
    # test an incorrect type of input
    with pytest.raises(pydantic.ValidationError):
        calculate_fractional_year_noaa("not a datetime object")

    # test an incorrect value of angle_output_units
    with pytest.raises(pydantic.ValidationError):
        calculate_fractional_year_noaa(datetime(year=2023, month=7, day=25, hour=12), angle_output_units="not a valid unit")


@pytest.mark.parametrize("timestamp_in_list, expected_fractional_year_in_list", cases_for_fractional_year_series_single_timestamp)
@pytest.mark.parametrize("tolerance", tolerances)
def test_calculate_fractional_year_time_series_noaa_single_timestamp(
    timestamp_in_list, expected_fractional_year_in_list, tolerance
):
    calculated = calculate_fractional_year_time_series_noaa(timestamp_in_list)
    assert isinstance(calculated, FractionalYear)
    assert pytest.approx(expected_fractional_year_in_list, abs=tolerance) == calculated.value
    assert RADIANS == calculated.unit


@pytest.mark.parametrize("timestamps, expected_fractional_year_series", cases_for_fractional_year_series)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_fractional_year_time_series_noaa(
    timestamps,
    expected_fractional_year_series,
    tolerance,
):
    calculated = calculate_fractional_year_time_series_noaa(timestamps)
    assert isinstance(calculated, np.ndarray)
    assert all(isinstance(calculation, FractionalYear) for calculation in calculated)
    assert np.allclose([item.value for item in calculated], expected_fractional_year_series, atol=tolerance)
    assert all(item.unit == RADIANS for item in calculated)


@pytest.mark.parametrize("timestamps, expected_fractional_year_series", cases_for_fractional_year_series)
@pytest.mark.parametrize('tolerance', tolerances)
def test_leap_year(
    timestamps,
    expected_fractional_year_series,
    tolerance,
):
    # 2024 is a leap year
    calculated = calculate_fractional_year_time_series_noaa(timestamps)
    assert isinstance(calculated, np.ndarray)
    assert all(isinstance(calculation, FractionalYear) for calculation in calculated)


def test_calculate_fractional_year_time_series_noaa_invalid_datetime():
    with pytest.raises(ValueError):
        calculate_fractional_year_time_series_noaa([]) # Empty list


@pytest.mark.parametrize("timestamps", timestamps)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_fractional_year_time_series_noaa_range(
    timestamps,
    tolerance,
):
    calculated = calculate_fractional_year_time_series_noaa(timestamps)
    assert all(0 <= calculation.value < 2 * np.pi for calculation in calculated)


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


@pytest.mark.parametrize("timestamps, expected_fractional_year_series", cases_for_fractional_year_series)
@pytest.mark.mpl_image_compare
def test_plot_fractional_year_time_series_noaa(timestamps, expected_fractional_year_series):
# def test_plot_fractional_year_noaa():
    calculated_fractional_year_series = calculate_fractional_year_time_series_noaa(timestamps)
    assert plot_fractional_year_noaa(
            timestamps,
            expected_fractional_year_series,
            calculated_fractional_year_series,
        )


@pytest.fixture
def expected_fractional_years_for_a_year(timestamps_for_a_year):
    return [calculate_fractional_year_noaa(timestamp).value for timestamp in timestamps_for_a_year]


@pytest.mark.mpl_image_compare
def test_plot_fractional_year_time_series_noaa(timestamps_for_a_year, expected_fractional_years_for_a_year):
# def test_plot_fractional_year_noaa():
    calculated_fractional_years_for_a_year = calculate_fractional_year_time_series_noaa(timestamps_for_a_year)
    assert plot_fractional_year_noaa(
            timestamps_for_a_year,
            expected_fractional_years_for_a_year,
            calculated_fractional_years_for_a_year,
        )
