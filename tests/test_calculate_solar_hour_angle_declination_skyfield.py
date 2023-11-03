import pytest
from pvgisprototype.algorithms.skyfield.solar_geometry import calculate_solar_hour_angle_declination_skyfield
from pvgisprototype import SolarHourAngle, SolarDeclination
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import HOUR_ANGLE_NAME, DECLINATION_NAME, RADIANS


test_cases_data = read_noaa_spreadsheet(
    './tests/data/test_cases_noaa_spreadsheet.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit=RADIANS,
    longitude='longitude',
    latitude='latitude',
    timestamp='timestamp',
    timezone='timezone',
    hour_angle=HOUR_ANGLE_NAME,
    declination=DECLINATION_NAME,
)
tolerances = [0.1]

@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone, expected_hour_angle,\
    expected_solar_declination, against_unit", test_cases,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_hour_angle_declination_skyfield(
    longitude,
    latitude,
    timestamp,
    timezone,
    against_unit,
    expected_hour_angle,
    expected_solar_declination,
    tolerance,
):
    calculated_hour_angle, calculated_solar_declination = calculate_solar_hour_angle_declination_skyfield(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
    )

    # Check types
    assert isinstance(calculated_hour_angle, SolarHourAngle)
    assert isinstance(calculated_solar_declination, SolarDeclination)

    # Assert output
    assert pytest.approx(
        getattr(expected_hour_angle, against_unit), tolerance) == getattr(calculated_hour_angle, against_unit)

    assert pytest.approx(
        getattr(expected_solar_declination, against_unit), tolerance) == getattr(calculated_solar_declination, against_unit)

    # Assert range

