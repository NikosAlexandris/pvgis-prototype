import pytest
import pytz
from typer.testing import CliRunner
from pvgisprototype.angular_loss_factor import calculate_angular_loss_factor
from pvgisprototype.direct_irradiance import calculate_refracted_solar_altitude
from pvgisprototype.direct_irradiance import calculate_optical_air_mass
from pvgisprototype.direct_irradiance import rayleigh_optical_thickness
from pvgisprototype.direct_irradiance import calculate_direct_normal_irradiance
from pvgisprototype.direct_irradiance import calculate_direct_horizontal_irradiance
from pvgisprototype.direct_irradiance import calculate_direct_inclined_irradiance
from pvgisprototype.direct_irradiance import app

def run_app(arguments):
    runner = CliRunner()
    result = runner.invoke(app, arguments)
    return result


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
    result = calculate_angular_loss_factor(solar_altitude, solar_declination)
    assert result == pytest.approx(expexted_angular_loss_factor)


@pytest.mark.parametrize(
    "latitude, elevation, timestamp, linke_turbidity_factor, expected_output", 
    [
        (40.085556, 2917.727, 0.2, '2023-06-22', 'Extraterrestrial irradiance: 1316.337133501784\nDirect normal irradiance: 1295.125350879713\nDirect horizontal irradiance: 1218.3216902511913\n'),
        ]
)
def test_calculate_direct_horizontal_irradiance(latitude, elevation, timestamp, linke_turbidity_factor, expected_output):
    arguments = [
        'horizontal',
        str(latitude),
        str(elevation),
        str(timestamp),
        str(linke_turbidity_factor),
    ]
    result = run_app(arguments)
    
    assert result.exit_code == 0
    assert expected_output in result.output


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


# def test_calculate_direct_horizontal_irradiance(mocker):
#     # Mocking imports and functions not defined in the current code
#     mocker.patch('main.calculate_solar_declination', return_value=0.1)
#     mocker.patch('main.calculate_solar_time', return_value=10)
#     mocker.patch('main.calculate_extraterrestrial_irradiance', return_value=1000)
#     mocker.patch('main.calculate_direct_normal_irradiance', return_value=500)
#     result = calculate_direct_horizontal_irradiance(45, 1000, 2023, 150, 5, 2)
#     assert isinstance(result, float)


@pytest.mark.parametrize(
    "latitude, elevation, timestamp, surface_tilt, surface_orientation, linke_turbidity_factor, method_for_solar_incidence_angle, expected_output",
    [
        (40.085556, 2917.727, '2023-06-22', 40, 180, 2, 'jenco', "Extraterrestrial irradiance: 1316.337133501784\nDirect normal irradiance: 1118.9581621543896\nDirect horizontal irradiance: 1052.6015867964556"),  # Mt Olympos
    ]
)
def test_calculate_direct_inclined_irradiance(latitude, elevation, timestamp, surface_tilt, surface_orientation, linke_turbidity_factor, method_for_solar_incidence_angle, expected_output):
    # Convert the parameters to strings to pass them as command-line arguments
    arguments = [
        'inclined',
        str(latitude),
        str(elevation),
        str(timestamp),
        str(surface_tilt),
        str(surface_orientation),
        str(linke_turbidity_factor),
        '-m',
        str(method_for_solar_incidence_angle),
    ]
    result = run_app(arguments)
    print(result) 
    # assert result.exit_code == 0
    assert expected_output in result.output
