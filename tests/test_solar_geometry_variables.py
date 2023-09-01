import pytest
import datetime
import numpy as np
import random
from pvgisprototype.api.data_structures import SolarGeometryDayConstants
from pvgisprototype.api.data_structures import SolarGeometryDayVariables
from pvgisprototype.algorithms.pvgis.solar_geometry import calculate_solar_time_pvgis
from pvgisprototype.algorithms.pvgis.solar_geometry import calculate_solar_geometry_pvgis_constants
from pvgisprototype.algorithms.pvgis.solar_geometry import calculate_solar_geometry_pvgis_variables
from pvgisprototype.plot.plot_solar_geometry_pvgis import plot_solar_geometry_pvgis_variables
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested


# Set a seed to ensure agreement of plots between tests!
random.seed(43) # Comment to really pick a random year
year = random.randint(2005, 2020)


def test_calculate_solar_time():
    # Replace values with really expected output
    year = 2005
    hour_of_year = 100
    expected_solar_time = 4
    calculated_solar_time = calculate_solar_time(year, hour_of_year)
    np.testing.assert_almost_equal(calculated_solar_time, expected_solar_time, decimal=2)


def test_convert_to_degrees_if_requested():
    
    angle_in_radians = np.pi
    expected_angle_in_degrees = 180
    converted_angle = convert_to_degrees_if_requested(angle_in_radians, 'degrees')
    assert converted_angle == expected_angle_in_degrees

    angle_in_radians = np.pi
    expected_angle_in_radians = np.pi
    converted_angle = convert_to_degrees_if_requested(angle_in_radians, 'radians')
    assert converted_angle == expected_angle_in_radians

# Arbitrary numbers/test cases -- Replaced with correct values
test_cases = [
        (
            SolarGeometryDayConstants(
                longitude=45.0,
                latitude=45.0,
                solar_declination=23.45,
                cosine_solar_declination=0.917,
                sine_solar_declination=0.398,
                lum_C11=0.123,
                lum_C13=0.456,
                lum_C22=0.789,
                lum_C31=0.987,
                lum_C33=0.654,
                sunrise_time=6.0,
                sunset_time=18.0,
                ),
            datetime.datetime(2023, 3, 21),
            SolarGeometryDayVariables(
                solar_altitude=45.0,
                sine_solar_altitude=0.707,
                tan_solar_altitude=1.0,
                solar_azimuth=90.0,
                sun_azimuth_angle=45.0,
                ),
            ),
        ]


@pytest.mark.parametrize(
    "solar_geometry_day_constants, timestamp, expected_output", test_cases
)
def test_calculate_solar_geometry_pvgis_variables(
        solar_geometry_day_constants,
        timestamp: datetime.datetime,
        expected_output,
        ):
    # variables = calculate_solar_geometry_variables(constants, output_units='degrees')
    variables = calculate_solar_geometry_pvgis_variables(
            solar_geometry_day_constants,
            timestamp,
            )
    assert isinstance(variables, SolarGeometryDayVariables), "Object should be an instance of SolarGeometryDayVariables"
    assert variables.sine_solar_altitude is not None, "sine_solar_altitude should not be None"
    assert variables.solar_altitude is not None, "solar_altitude should not be None"
    assert variables.solar_azimuth is not None, "solar_azimuth should not be None"
    assert variables.sun_azimuth_angle is not None, "sun_azimuth_angle should not be None"
    assert variables.tan_solar_altitude is not None, "tan_solar_altitude should not be None"
    # assert variables.sine_solar_altitude == -0.20678356693662208


location_and_time = [
        (0,  0, datetime.datetime(2023, 1, 1), datetime.datetime(2024, 1, 1)), 
        (0, 30, datetime.datetime(2023, 1, 1), datetime.datetime(2024, 1, 1)),
        (0, 45, datetime.datetime(2023, 1, 1), datetime.datetime(2024, 1, 1)),
        (0, 60, datetime.datetime(2023, 1, 1), datetime.datetime(2024, 1, 1)),
]
@pytest.mark.parametrize("longitude, latitude, start_date, end_date", location_and_time)
@pytest.mark.mpl_image_compare
def test_solar_geometry_pvgis_variables_plot(longitude: float, latitude: float, start_date: datetime.datetime, end_date: datetime.datetime):
    return plot_solar_geometry_pvgis_variables(
            longitude,
            latitude,
            start_date,
            end_date,
            )

# @pytest.mark.mpl_image_compare
# def test_solar_geometry_variables_plot():
#     return plot_solar_geometry_pvgis_variables(45, 1, 365)

# @pytest.mark.mpl_image_compare
# def test_solar_geometry_variables_plot():
#     return plot_solar_geometry_pvgis_variables(90, 1, 365)
