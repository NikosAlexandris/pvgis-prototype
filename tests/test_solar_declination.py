import pytest
from pvgisprototype.solar_declination import calculate_solar_declination
from pvgisprototype.solar_declination_plot import plot_solar_declination
import matplotlib.pyplot as plt
import numpy as np


# Arbitrary test cases -- Replaced with correct values
@pytest.mark.parametrize(
    "day_in_year, expected", 
    [
        (10, 0.3833890030449887),
        (182, -0.40343635275536255)  # Test for day 182, half the year, where the solar constant should be minimum
    ]
)
def test_calculate_solar_declination(day_in_year: int, expected: float):
    assert pytest.approx(calculate_solar_declination(day_in_year), 0.0001) == expected


# a decorator to instruct using the baseline image
@pytest.mark.mpl_image_compare
def test_solar_declination_plot():
    return plot_solar_declination()
