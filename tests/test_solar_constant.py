import pytest
from pvgisprototype.solar_constant import calculate_solar_constant
from pvgisprototype.solar_constant_plot import plot_solar_constant
import matplotlib.pyplot as plt
import numpy as np


# Arbitrary test cases -- Replaced with correct values
@pytest.mark.parametrize(
    "day_in_year, expected", 
    [
        (10, 1412.366252486348),
        (182, 1321.44578929)  # Test for day 182, half the year, where the value should be minimum
    ]
)
def test_calculate_solar_constant(day_in_year: int, expected: float):
    assert pytest.approx(calculate_solar_constant(day_in_year), 0.0001) == expected


# a decorator to instruct using the baseline image
@pytest.mark.mpl_image_compare
def test_solar_constant_plot():
    return plot_solar_constant()
