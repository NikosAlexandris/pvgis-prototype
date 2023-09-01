import pytest
from datetime import datetime
import matplotlib.pyplot as plt
from pvgisprototype.api.irradiance.extraterrestrial import calculate_extraterrestrial_normal_irradiance
from pvgisprototype.constants import EXTRATERRESTRIAL_IRRADIANCE_MIN
from pvgisprototype.constants import EXTRATERRESTRIAL_IRRADIANCE_MAX
# from pvgisprototype.plot.plot_extraterrestrial_irradiance import plot_extraterrestrial_irradiance
import numpy as np
import random

tolerances = [1, 0, 0.5, 0.1, 0.01, 0.001, 0.0001]
@pytest.mark.parametrize(
    "timestamp, expected", 
    [
        (datetime(year=2023, month=1, day=3, hour=12, minute=0, second=0), 1412.366252486348),  # Perihelion
        (datetime(year=2023, month=3, day=21, hour=12, minute=0, second=0), 1361.44578929),  # Vernal equinox
        (datetime(year=2023, month=7, day=2, hour=12, minute=0, second=0), 1321.44578929),  # Aphelion
        (datetime(year=2023, month=9, day=23, hour=12, minute=0, second=0), 1361.44578929),  # Autumnal equinox
        (datetime(year=2023, month=12, day=21, hour=12, minute=0, second=0), 1400.25687453),  # Close to winter solstice
    ]
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_extraterrestrial_irradiance(timestamp: datetime, expected: float, tolerance: float):
    assert expected == pytest.approx(calculate_extraterrestrial_normal_irradiance(timestamp), tolerance)

random_timestamp = [
        datetime(year=random.randint(2005, 2023), month=random.randint(1, 12), day=random.randint(1, 28), hour=random.randint(0, 23), minute=random.randint(0, 59), second=random.randint(0, 59)),
        datetime(year=random.randint(2005, 2023), month=random.randint(1, 12), day=random.randint(1, 28), hour=random.randint(0, 23), minute=random.randint(0, 59), second=random.randint(0, 59)),
        datetime(year=random.randint(2005, 2023), month=random.randint(1, 12), day=random.randint(1, 28), hour=random.randint(0, 23), minute=random.randint(0, 59), second=random.randint(0, 59)),
        datetime(year=random.randint(2005, 2023), month=random.randint(1, 12), day=random.randint(1, 28), hour=random.randint(0, 23), minute=random.randint(0, 59), second=random.randint(0, 59)),
        datetime(year=random.randint(2005, 2023), month=random.randint(1, 12), day=random.randint(1, 28), hour=random.randint(0, 23), minute=random.randint(0, 59), second=random.randint(0, 59)),
    ]
@pytest.mark.parametrize('timestamp', random_timestamp) 
def test_calculate_extraterrestrial_irradiance_for_random_day(timestamp: datetime):
    calculated = calculate_extraterrestrial_normal_irradiance(timestamp)
    assert EXTRATERRESTRIAL_IRRADIANCE_MIN <= calculated <= EXTRATERRESTRIAL_IRRADIANCE_MAX


# @pytest.mark.mpl_image_compare  # instructs use of a baseline image
# def test_extraterrestrial_irradiance_plot():
#     return plot_extraterrestrial_irradiance()
