import pytest
from pvgisprototype.solar_declination import calculate_solar_declination
from pvgisprototype.solar_declination_plot import plot_solar_declination
from pvgisprototype.solar_declination_plot import plot_solar_declination_one_year
from pvgisprototype.solar_declination_plot import plot_solar_declination_five_years
import matplotlib.pyplot as plt
import numpy as np
import random


"""
The solar declination is the angle between the rays of the Sun and the plane of
the Earth's equator. Its value varies between -23.44° and +23.44°
(approximately) throughout the year due to the tilt of the Earth's axis.

Verify expected declination for these days based on a given formula or lookup table
"""


@pytest.mark.parametrize(
    "day_of_year, expected", 
    [
        (1, -23.44),  # Around New Year
        (79, 0),  # Around vernal equinox
        (172, 23.44),  # Around summer solstice
        (266, 0),  # Around autumnal equinox
        (355, -23.44),  # Around winter solstice
    ]
)
def test_calculate_solar_declination(day_of_year: int, expected: float):
    # assert pytest.approx(calculate_solar_declination(day_of_year, output_units='radians'), 0.0001) == expected
    # assert pytest.approx(calculate_solar_declination(day_of_year, output_units='degrees'), 1) == expected
    # assert pytest.approx(calculate_solar_declination(day_of_year, output_units='degrees'), 0.) == expected
    assert pytest.approx(calculate_solar_declination(day_of_year, output_units='degrees'), 0.1) == expected
    assert pytest.approx(calculate_solar_declination(day_of_year, output_units='degrees'), 0.01) == expected
    assert pytest.approx(calculate_solar_declination(day_of_year, output_units='degrees'), 0.001) == expected
    assert pytest.approx(calculate_solar_declination(day_of_year, output_units='degrees'), 0.0001) == expected


# @pytest.mark.mpl_image_compare  # instructs use of a baseline image
# def test_solar_declination_plot():
#     return plot_solar_declination()


# Set a seed to ensure agreement of plots between tests!
random.seed(43) # Comment to really pick a random year
random_year = random.randint(2005, 2023)
@pytest.mark.mpl_image_compare  # instructs use of a baseline image
def test_solar_declination_plot_one_year():
    return plot_solar_declination_one_year(year=random_year, title=f'Solar Declination {random_year}')


# @pytest.mark.mpl_image_compare
# def test_solar_declination_plot_five_years():
#     return plot_solar_declination(start_year=2018, end_year=2022, title='Solar Declination 2018-2022')
