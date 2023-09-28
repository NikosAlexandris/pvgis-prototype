import pytest
from typer.testing import CliRunner
from pvgisprototype.api.irradiance.loss import calculate_angular_loss_factor_for_direct_irradiance
from pvgisprototype.api.irradiance.loss import calculate_angular_loss_factor_for_nondirect_irradiance
from pvgisprototype.api.irradiance.direct import calculate_refracted_solar_altitude
from pvgisprototype.api.irradiance.direct import calculate_optical_air_mass
from pvgisprototype.api.irradiance.direct import calculate_rayleigh_optical_thickness
from pvgisprototype.api.irradiance.direct import calculate_direct_normal_irradiance
from pvgisprototype.api.irradiance.direct import calculate_direct_horizontal_irradiance
from pvgisprototype.api.irradiance.direct import calculate_direct_inclined_irradiance_pvgis
from pvgisprototype.api.irradiance.direct import app


def run_app(arguments):
    runner = CliRunner()
    result = runner.invoke(app, arguments)
    return result


# @pytest.mark.parametrize(
#     "latitude, elevation, timestamp, linke_turbidity_factor, expected_output", 
#     [
#         (40.085556, 2917.727, 0.2, '2023-06-22', 'Extraterrestrial irradiance: 1316.337133501784\nDirect normal irradiance: 1295.125350879713\nDirect horizontal irradiance: 1218.3216902511913\n'),
#         ]
# )
# def test_calculate_direct_horizontal_irradiance(latitude, elevation, timestamp, linke_turbidity_factor, expected_output):
#     arguments = [
#         'horizontal',
#         str(latitude),
#         str(elevation),
#         str(timestamp),
#         str(linke_turbidity_factor),
#     ]
#     result = run_app(arguments)
    
#     assert result.exit_code == 0
#     assert expected_output in result.output


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

locations = [ 
    (40.085556, 2917.727, '2023-06-22'),  # Mt Olympos
    (0, 40, 2000),  # Another location
]

other_parameters = [ 
    (40, 180, 2, 'jenco', 
    "Extraterrestrial irradiance: 1316.337133501784\nDirect normal irradiance: 1118.9581621543896\nDirect horizontal irradiance: 1052.6015867964556"),  
    # (2, 30, 180, 'simple', 
    # 'Direct inclined irradiance: XXX (based on simple)\n'),
]

@pytest.mark.parametrize(
    "location, parameters",
    list(zip(locations, other_parameters))
)
def test_calculate_direct_inclined_irradiance_pvgis(location, parameters):
    longitude, latitude, elevation = location
    linke_turbidity_factor, surface_tilt, surface_orientation, solar_incidence_angle_model, expected_output = parameters
    arguments = [
        'inclined',
        str(longitude),
        str(latitude),
        str(elevation),
        # str(timestamp),
        '--linke-turbidity-factor',
        str(linke_turbidity_factor),
        '--surface-tilt',
        str(surface_tilt),
        '--surface-orientation',
        str(surface_orientation),
        '--incidence-angle-model',
        solar_incidence_angle_model,
    ]
    result = run_app(arguments)
    assert result.exit_code == 0
    assert expected_output in result.output
