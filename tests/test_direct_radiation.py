import pytest
from pvgisprototype.direct_radiation import apply_angular_loss
from pvgisprototype.direct_radiation import calculate_direct_radiation_for_tilted_surface


@pytest.mark.parametrize(
    "direct_radiation, solar_altitude, incidence_angle, expected_result",
    # Edge cases 
    [
        (100, 0, 0, 0), # Solar altitude & incidence angle at 0 : expected radiation is 0
        (100, 90, 90, 100), # Solar altitude & incidence angle at 90
        (100, 45, 45, 100), # Solar altitude & incidence angle equal
        (0, 45, 45, 0), # Direct radiation at 0
    ]
)
def test_apply_angular_loss(direct_radiation, solar_altitude, incidence_angle, expected_result):
    result = apply_angular_loss(direct_radiation, solar_altitude, incidence_angle)
    assert result == pytest.approx(expected_result)


@pytest.mark.parametrize(
    "direct_radiation_coefficient, solar_altitude, sine_of_solar_altitude, incidence_angle_index, expected_result",
    [
        (0, 0, 0, 0, 0), # All parameters at 0
        (0.5, 30, 0.5, 0, 0), # Minimum values for each parameter
        (1, 90, 1, 1, 90), # Maximum values for each parameter
        (0.85, 45, 0.707, 1, 420), # Typical values
    ]
)
def test_calculate_direct_radiation_for_tilted_surface(
        direct_radiation_coefficient,
        solar_altitude,
        sine_of_solar_altitude,
        incidence_angle_index,
        expected_result
        ):
    result = calculate_direct_radiation_for_tilted_surface(
            direct_radiation_coefficient,
            solar_altitude,
            sine_of_solar_altitude,
            incidence_angle_index
            )
    assert result == pytest.approx(expected_result)
