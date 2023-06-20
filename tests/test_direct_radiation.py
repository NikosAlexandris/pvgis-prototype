import pytest
from pvgisprototype.angular_loss_factor import calculate_angular_loss_factor
from pvgisprototype.direct_irradiance import calculate_refracted_solar_altitude
from pvgisprototype.direct_irradiance import calculate_optical_air_mass
from pvgisprototype.direct_irradiance import rayleigh_optical_thickness
from pvgisprototype.direct_irradiance import calculate_direct_normal_irradiance
from pvgisprototype.direct_irradiance import calculate_direct_horizontal_irradiance
from pvgisprototype.direct_irradiance import calculate_direct_inclined_irradiance


@pytest.mark.parametrize(
    "solar_altitude, solar_declination, expexted_angular_loss_factor",
    [
        (-1000, 90, 0),  # Negative direct radiation
        (1000, -90, 0),  # Negative solar altitude
        (1000, 90, -30),  # Negative incidence angle
    ]
)
def test_calculate_angular_loss_factor_with_invalid_inputs(solar_altitude, solar_declination, expexted_angular_loss_factor):
    with pytest.raises(ValueError):
        calculate_angular_loss_factor(solar_altitude, solar_declination)


@pytest.mark.parametrize(
    "solar_altitude, solar_declination, expexted_angular_loss_factor",
    # Edge cases 
    [
        (1000, 90, 0),
        (0, 45, 45),  # Direct radiation at 0
        (100, 0, 0),  # Solar altitude & incidence angle at 0 : expected radiation is 0
        (100, 45, 45),  # Solar altitude & incidence angle equal
        (100, 90, 90),  # Solar altitude & incidence angle at 90
        (600, 60, 30), 
        (800, 30, 40),  
        (800, 45, 45),
        (1200, 20, 60),
    ]
)
def test_calculate_angular_loss_factor(solar_altitude, solar_declination, expexted_angular_loss_factor):
    result = calculate_angular_loss_factor(direct_radiation, solar_altitude, incidence_angle)
    assert result == pytest.approx(expected_result)


@pytest.mark.parametrize(
    "direct_radiation, direct_radiation_coefficient, solar_altitude, incidence_angle_index, expected_result",
    [
        (0, 0, 0, 0, 0),  # All parameters at 0
        (1, 0.0, 0.0, 0, 0),  # Minimum direct radiation with coefficient, solar altitude, and incidence angle set to 0, expected result is 0
        (500, 0.5, 30, 1, 29.95266075017529),
        (600, 0.6, 60, 0, 5.292740994406696),
        (800, 0.85, 45, 1, 420),
        (1000, 0.85, 45, 1, 54.016467406610325),
        (1000, 0.8, 45, 0, 4.716948972727759e+271),
        (1361, 1, 90, 1, 1361),
    ]
)

# def test_calculate_refracted_solar_altitude():
#     result = calculate_refracted_solar_altitude(0.5)
#     assert isinstance(result, float)


# def test_calculate_optical_air_mass():
#     result = calculate_optical_air_mass(1000, 0.5)
#     assert isinstance(result, float)


# def test_rayleigh_optical_thickness():
#     result = rayleigh_optical_thickness(10)
#     assert isinstance(result, float)


# def test_calculate_direct_normal_irradiance():
#     result = calculate_direct_normal_irradiance(1361, 2, 1)
#     assert isinstance(result, float)


def test_calculate_direct_horizontal_irradiance(mocker):
    # Mocking imports and functions that are not defined in the current code
    mocker.patch('main.calculate_solar_declination', return_value=0.1)
    mocker.patch('main.calculate_solar_time', return_value=10)
    mocker.patch('main.calculate_extraterrestrial_irradiance', return_value=1000)
    mocker.patch('main.calculate_direct_normal_irradiance', return_value=500)
    result = calculate_direct_horizontal_irradiance(45, 1000, 2023, 150, 5, 2)
    assert isinstance(result, float)

def test_calculate_direct_inclined_irradiance(
        direct_radiation,
        direct_radiation_coefficient,
        solar_altitude,
        incidence_angle_index,
        expected_result
        ):
    result = calculate_direct_radiation_for_tilted_surface(
            direct_radiation,
            direct_radiation_coefficient,
            solar_altitude,
            incidence_angle_index,
            )
    assert result == pytest.approx(expected_result)
