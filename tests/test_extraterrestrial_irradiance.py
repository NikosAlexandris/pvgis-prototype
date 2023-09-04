import pytest
from datetime import datetime
import matplotlib.pyplot as plt
from pvgisprototype.api.irradiance.extraterrestrial import calculate_extraterrestrial_normal_irradiance
from pvgisprototype.constants import EXTRATERRESTRIAL_IRRADIANCE_MIN
from pvgisprototype.constants import EXTRATERRESTRIAL_IRRADIANCE_MAX
from pvgisprototype.plot.plot_extraterrestrial_irradiance import plot_extraterrestrial_irradiance
import numpy as np
from .cases.extraterrestrial_irradiance import tolerances
from .cases.extraterrestrial_irradiance import cases_for_extraterrestrial_irradiance
from .cases.extraterrestrial_irradiance import random_timestamp
import random


@pytest.mark.parametrize("timestamp, expected", cases_for_extraterrestrial_irradiance)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_extraterrestrial_irradiance(timestamp: datetime, expected: float, tolerance: float):
    assert pytest.approx(expected, tolerance) == calculate_extraterrestrial_normal_irradiance(timestamp)


@pytest.mark.parametrize('timestamp', random_timestamp) 
def test_calculate_extraterrestrial_irradiance_for_random_day(timestamp: datetime):
    calculated = calculate_extraterrestrial_normal_irradiance(timestamp)
    assert EXTRATERRESTRIAL_IRRADIANCE_MIN <= calculated <= EXTRATERRESTRIAL_IRRADIANCE_MAX


# Set a seed to ensure agreement of plots between tests!
random.seed(43) # Comment to really pick a random year
random_year = random.randint(2005, 2023)
print(f'Random year : {random_year}')
@pytest.mark.mpl_image_compare  # use a baseline image
def test_extraterrestrial_irradiance_plot(year=random_year):
    return plot_extraterrestrial_irradiance(year)
