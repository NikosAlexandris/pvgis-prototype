import pytest
from pvgisprototype.algorithms.pvlib.solar_hour_angle import calculate_solar_hour_angle_pvlib
from pvgisprototype import SolarHourAngle
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import HOUR_ANGLE_NAME, DEGREES


test_cases_data = read_noaa_spreadsheet(
    './tests/cases/noaa.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit=DEGREES,
    longitude='longitude',
    timestamp='timestamp',
    hour_angle=HOUR_ANGLE_NAME,
)

tolerances = [0.1]

@pytest.mark.parametrize(
    "longitude, timestamp, expected_hour_angle, against_unit",
    test_cases,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_hour_angle_pvlib(
    longitude,
    timestamp,
    expected_hour_angle,
    against_unit,
    tolerance,
):
    calculated_hour_angle = calculate_solar_hour_angle_pvlib(
        longitude=longitude,
        timestamp=timestamp,
    )

    # Check types
    assert isinstance(calculated_hour_angle, SolarHourAngle)

    # Assert output
    assert pytest.approx(
        getattr(expected_hour_angle, against_unit), tolerance) == getattr(calculated_hour_angle, against_unit)

    # Assert range

