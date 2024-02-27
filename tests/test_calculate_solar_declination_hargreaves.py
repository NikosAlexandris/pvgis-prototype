import pytest
from pvgisprototype.algorithms.hargreaves.solar_declination import calculate_solar_declination_hargreaves
from pvgisprototype import SolarDeclination
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import DECLINATION_NAME, RADIANS


test_cases_data = read_noaa_spreadsheet(
    './tests/cases/noaa.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit=RADIANS,
    timestamp='timestamp',
    declination=DECLINATION_NAME,
)

tolerances = [0.1]

@pytest.mark.parametrize(
    "timestamp, expected_solar_declination, against_unit",
    test_cases,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_declination_hargreaves(
    timestamp,
    against_unit,
    expected_solar_declination,
    tolerance,
):
    calculated_solar_declination = calculate_solar_declination_hargreaves(
        timestamp=timestamp,
    )

    # Check types
    assert isinstance(calculated_solar_declination, SolarDeclination)

    # Assert output
    assert pytest.approx(
        getattr(expected_solar_declination, against_unit), tolerance) == getattr(calculated_solar_declination, against_unit)
