import random
import pytest
from pvgisprototype.data_structures import SolarGeometryDayConstants
from pvgisprototype.data_structures import SolarGeometryDayVariables
from pvgisprototype.solar_geometry_variables import convert_to_degrees_if_requested
from pvgisprototype.solar_geometry_variables import calculate_solar_time
from pvgisprototype.solar_geometry_constants import calculate_solar_geometry_constants
from pvgisprototype.solar_geometry_variables import calculate_solar_geometry_variables
from pvgisprototype.solar_geometry_variables_plot import plot_solar_geometry_variables
import numpy as np


# Set a seed to ensure agreement of plots between tests!
random.seed(43) # Comment to really pick a random year
year = random.randint(2005, 2020)


def test_calculate_solar_time():
    # For a given set of inputs, check that the function returns the expected output.
    # You would need to replace these values with ones that you know the expected output for.
    year = 2005
    hour_of_year = 100
    expected_solar_time = 4  # Replace with expected solar time
    calculated_solar_time = calculate_solar_time(year, hour_of_year)
    np.testing.assert_almost_equal(calculated_solar_time, expected_solar_time, decimal=2)


def test_convert_to_degrees_if_requested():
    # Check that the function correctly converts from radians to degrees when requested.
    angle_in_radians = np.pi
    expected_angle_in_degrees = 180
    converted_angle = convert_to_degrees_if_requested(angle_in_radians, 'degrees')
    assert converted_angle == expected_angle_in_degrees

    # Check that the function correctly leaves the angle in radians when requested.
    angle_in_radians = np.pi
    expected_angle_in_radians = np.pi
    converted_angle = convert_to_degrees_if_requested(angle_in_radians, 'radians')
    assert converted_angle == expected_angle_in_radians

# Arbitrary numbers/test cases -- Replaced with correct values
test_cases = [
    (
        SolarGeometryDayConstants(
            latitude=45.0,
            solar_declination=23.45,
            cosine_of_solar_declination=0.917,
            sine_of_solar_declination=0.398,
            lum_C11=0.123,
            lum_C13=0.456,
            lum_C22=0.789,
            lum_C31=0.987,
            lum_C33=0.654,
            sunrise_time=6.0,
            sunset_time=18.0,
        ),
        year,  # Input year
        100,  # Input hour_of_year
        # Expected output
        SolarGeometryDayVariables(
            solar_altitude=45.0,
            sine_of_solar_altitude=0.707,
            tan_of_solar_altitude=1.0,
            solar_azimuth=90.0,
            sun_azimuth_angle=45.0,
        )
    ),
    # Add more test cases
]

@pytest.mark.parametrize(
    "solar_geometry_day_constants, year, hour_of_year, expected_output", test_cases
)
def test_calculate_solar_geometry_variables(
        solar_geometry_day_constants,
        year,
        hour_of_year,
        expected_output,
        ):
    # variables = calculate_solar_geometry_variables(constants, output_units='degrees')
    variables = calculate_solar_geometry_variables(
            solar_geometry_day_constants,
            year,
            hour_of_year = 100
            )
    assert isinstance(variables, SolarGeometryDayVariables), "Object should be an instance of SolarGeometryDayVariables"
    assert variables.sine_of_solar_altitude is not None, "sine_of_solar_altitude should not be None"
    assert variables.solar_altitude is not None, "solar_altitude should not be None"
    assert variables.solar_azimuth is not None, "solar_azimuth should not be None"
    assert variables.sun_azimuth_angle is not None, "sun_azimuth_angle should not be None"
    assert variables.tan_of_solar_altitude is not None, "tan_of_solar_altitude should not be None"
    # assert variables.sine_of_solar_altitude == -0.20678356693662208


@pytest.mark.mpl_image_compare
def test_solar_geometry_variables_plot():
    return plot_solar_geometry_variables(0, year, 1, 365)

# @pytest.mark.mpl_image_compare
# def test_solar_geometry_variables_plot():
#     return plot_solar_geometry_variables(45, 1, 365)

# @pytest.mark.mpl_image_compare
# def test_solar_geometry_variables_plot():
#     return plot_solar_geometry_variables(90, 1, 365)
