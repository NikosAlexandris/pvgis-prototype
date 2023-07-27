import pytest
import matplotlib.pyplot as plt
from pvgisprototype.api.geometry.solar_declination import calculate_solar_declination
from pvgisprototype.plot.plot_solar_declination import plot_solar_declination
from pvgisprototype.plot.plot_solar_declination import plot_solar_declination
from pvgisprototype.plot.plot_solar_declination import plot_solar_declination_five_years
import numpy as np
import random
import datetime


"""
The solar declination is the angle between
the rays of the Sun and the plane of the Earth's equator.
Its value varies between -23.44° and +23.44° (approximately)
throughout the year due to the tilt of the Earth's axis.

Verify expected solar declination angles for the listed days
based on a given formula or lookup table ?
"""


test_cases = [
    (datetime.datetime(2023, 1, 1), -23.38044),  # Around vernal equinox
    (datetime.datetime(2023, 3, 20), 0),  # Around vernal equinox
    (datetime.datetime(2023, 3, 21), 0),  # Around vernal equinox
    (datetime.datetime(2023, 6, 20), 23.44),  # Around summer solstice
    (datetime.datetime(2023, 6, 21), 23.44),  # Around summer solstice
    (datetime.datetime(2023, 9, 22), 0),  # Around autumnal equinox
    (datetime.datetime(2023, 9, 23), 0),  # Around autumnal equinox
    (datetime.datetime(2023, 12, 21), -23.44),  # Around winter solstice
    (datetime.datetime(2023, 12, 22), -23.44),  # Around winter solstice
    (datetime.datetime(2023, 12, 30), -16.428456),  # Around winter solstice
]
tolerances = [1, 0.1]
@pytest.mark.parametrize( "timestamp, expected", test_cases)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_declination(
        timestamp: datetime.datetime,
        expected: float,
        tolerance: float,
        ):
    assert expected == pytest.approx(
        calculate_solar_declination(
            timestamp=timestamp,
            timezone=None,
            angle_output_units="degrees",
        ),
        tolerance,
    )
    # assert pytest.approx(calculate_solar_declination(timestamp, output_units='degrees'), 0.1) == expected


# Set a seed to ensure agreement of plots between tests!
random.seed(43) # Comment to really pick a random year
random_year = random.randint(2005, 2023)
@pytest.mark.mpl_image_compare  # instructs use of a baseline image
def test_plot_solar_declination():
    assert plot_solar_declination(
            # start_date,
            # end_date,
            year=random_year,
            title=f'Solar Declination {random_year}',
            output_units='degrees',
            )


random_year = random.randint(2005, 2023)
@pytest.mark.mpl_image_compare
def test_plot_solar_declination_five_years():
    assert plot_solar_declination_five_years(
            start_year=random_year,
            title="Five-Year Variation of Solar Declination",
            output_units='degrees',
            )
