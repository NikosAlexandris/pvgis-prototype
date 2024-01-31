import pytest
from pvgisprototype.api.irradiance.direct import calculate_refracted_solar_altitude_time_series
from pvgisprototype import SolarAltitude
import numpy as np
from pvgisprototype.constants import RADIANS, DEGREES


tolerances = [1, 0, 0.5, 0.1, 0.01, 0.001, 0.0001]
@pytest.mark.parametrize(
    "input_solar_altitude_values, expected_solar_altitude_values, angle_input_units, angle_output_units",
    [
        (
            [30.0, 40.0, 50.0],
            [30.1, 40.1, 50.1],
            DEGREES,
            RADIANS,
        ),  # Add more test cases as needed
    ],
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_refracted_solar_altitude_time_series(
    input_solar_altitude_values,
    expected_solar_altitude_values,
    angle_input_units,
    angle_output_units,
    tolerance,
):
    input_solar_altitude_series = np.array(
        [
            SolarAltitude(value=value, unit=angle_input_units)
            for value in input_solar_altitude_values
        ],
        dtype=object,
    )

    calculated_refracted_solar_altitude_series = calculate_refracted_solar_altitude_time_series(
        input_solar_altitude_series,
        angle_input_units,
        angle_output_units,
    )
    calculated_values = [item.value for item in calculated_refracted_solar_altitude_series]

    assert len(expected_solar_altitude_values) == len(calculated_values)
    assert np.allclose(expected_solar_altitude_values, calculated_values, atol=tolerance)
