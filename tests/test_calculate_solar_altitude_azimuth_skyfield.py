import pytest
from pvgisprototype.algorithms.skyfield.solar_geometry import calculate_solar_altitude_azimuth_skyfield
from pvgisprototype import SolarAltitude, SolarAzimuth
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import ALTITUDE_NAME, AZIMUTH_NAME


test_cases_data = read_noaa_spreadsheet(
    './tests/data/test_cases_noaa_spreadsheet.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit='radians',
    longitude='longitude',
    latitude='latitude',
    timestamp='timestamp',
    timezone='timezone',
    altitude=ALTITUDE_NAME,
    azimuth=AZIMUTH_NAME,
)
tolerances = [0.1]

@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone, expected_hour_angle,\
    expected_solar_declination, against_unit", test_cases,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_altitude_azimuth_skyfield(
    longitude,
    latitude,
    timestamp,
    timezone,
    against_unit,
    expected_hour_angle,
    expected_solar_declination,
    tolerance,
):
    calculated_hour_angle, calculated_solar_declination = calculate_solar_altitude_azimuth_skyfield(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
    )

    # Check types
    assert isinstance(calculated_hour_angle, SolarAltitude)
    assert isinstance(calculated_solar_declination, SolarAzimuth)

    # Assert output
    assert pytest.approx(
        getattr(expected_hour_angle, against_unit), tolerance) == getattr(calculated_hour_angle, against_unit)

    assert pytest.approx(
        getattr(expected_solar_declination, against_unit), tolerance) == getattr(calculated_solar_declination, against_unit)

    # Assert range

