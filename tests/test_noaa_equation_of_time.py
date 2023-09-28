import pytest
from datetime import datetime
from pvgisprototype.algorithms.noaa.equation_of_time import calculate_equation_of_time_noaa
from pvgisprototype.algorithms.noaa.equation_of_time import calculate_equation_of_time_time_series_noaa
from pvgisprototype.algorithms.noaa.equation_of_time import EquationOfTime
import numpy as np
from .cases.equation_of_time import cases_for_equation_of_time
from .cases.equation_of_time import tolerances


@pytest.mark.parametrize("timestamp, time_output_units, expected", cases_for_equation_of_time)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_equation_of_time_noaa(
    timestamp, time_output_units, expected, tolerance
):
    calculated = calculate_equation_of_time_noaa(timestamp, time_output_units)
    assert pytest.approx(expected, abs=tolerance) == calculated.value
    assert time_output_units == calculated.unit


@pytest.mark.parametrize("timestamp, time_output_units, expected", cases_for_equation_of_time)
def test_calculate_equation_of_time_time_series_noaa_single_timestamp(timestamp, time_output_units, expected):
    calculated = calculate_equation_of_time_time_series_noaa(timestamp)
    assert isinstance(calculated, EquationOfTime)
    assert time_output_units == calculated.unit


@pytest.fixture
def timestamps():
    return [
        datetime(2022, 3, 20, 12),
        datetime(2022, 6, 21, 12),
        datetime(year=2023, month=7, day=25, hour=12),
        datetime(year=2023, month=1, day=1, hour=0),
        datetime(year=2023, month=12, day=31, hour=23),
    ]


def test_calculate_equation_of_time_time_series_noaa(
    timestamps
):
    calculated = calculate_equation_of_time_time_series_noaa(timestamps)
    assert isinstance(calculated, np.ndarray)
    assert all(isinstance(calculation, EquationOfTime) for calculation in calculated)


def test_calculate_equation_of_time_time_series_noaa_range(
    timestamps
):
    calculated = calculate_equation_of_time_time_series_noaa(timestamps)
    assert all(-20 <= calculation.value <= 20 for calculation in calculated)


def test_invalid_datetime_equation_of_time():
    with pytest.raises(ValueError):
        calculate_equation_of_time_time_series_noaa([])  # Empty list
