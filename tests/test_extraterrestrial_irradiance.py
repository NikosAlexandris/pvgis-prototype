import pytest
import matplotlib.pyplot as plt
from pvgisprototype.api.irradiance.extraterrestrial import calculate_extraterrestrial_normal_irradiance
from pvgisprototype.constants import EXTRATERRESTRIAL_IRRADIANCE_MIN
from pvgisprototype.constants import EXTRATERRESTRIAL_IRRADIANCE_MAX
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
    ]
)
def test_calculate_extraterrestrial_irradiance(day_of_year: int, expected: float):
    assert expected == pytest.approx(calculate_extraterrestrial_irradiance(day_of_year), 0.0001)


@pytest.mark.parametrize(
    "day_of_year", 
    [
        # (random.randint(1, 366), 1360.8931954516274)  # Random day of the year
        (random.randint(1, 366)),
        (random.randint(1, 366)),
        (random.randint(1, 366)),
        (random.randint(1, 366)),
        (random.randint(1, 366)),
    ]
)
def test_calculate_extraterrestrial_irradiance_for_random_day(day_of_year: int):
    calculated = calculate_extraterrestrial_irradiance(day_of_year)
    # assert expected == pytest.approx(calculated, abs=0.5)
    assert EXTRATERRESTRIAL_IRRADIANCE_MIN <= calculated <= EXTRATERRESTRIAL_IRRADIANCE_MAX


# @pytest.mark.mpl_image_compare  # instructs use of a baseline image
# def test_extraterrestrial_irradiance_plot():
#     return plot_extraterrestrial_irradiance()
