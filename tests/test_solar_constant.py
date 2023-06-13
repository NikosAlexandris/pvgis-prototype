import pytest
from pvgisprototype.solar_constant import calculate_solar_constant
from pvgisprototype.solar_constant_plot import plot_solar_constant
import matplotlib.pyplot as plt
import numpy as np
import random


@pytest.mark.parametrize(
    "day_of_year, expected", 
    [
        (3, 1412.366252486348),   # Perihelion: solar constant should be maximum
        (80, 1361.44578929),  # Vernal equinox
        (183, 1321.44578929),  # Aphelion: solar constant should be minimum
        (266, 1361.44578929),  # Autumnal equinox
        (355, 1400.25687453),  # Close to winter solstice
        (random.randint(1, 365), 1361.44578929)  # Random day of the year
    ]
)
def test_calculate_solar_constant(day_of_year: int, expected: float):
    assert pytest.approx(calculate_solar_constant(day_of_year), 0.0001) == expected


@pytest.mark.mpl_image_compare  # instructs use of a baseline image
def test_solar_constant_plot():
    return plot_solar_constant()
