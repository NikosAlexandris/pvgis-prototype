import pytest
from pvgisprototype.algorithms.pvlib.solar_azimuth import calculate_solar_azimuth_pvlib
from pvgisprototype import SolarAzimuth
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import AZIMUTH_NAME, DEGREES


test_cases_data = read_noaa_spreadsheet(
    './tests/data/test_cases_noaa_spreadsheet.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit=DEGREES,
    longitude='longitude',
    latitude='latitude',
    timestamp='timestamp',
    timezone='timezone',
    azimuth=AZIMUTH_NAME,
)

tolerances = [0.1]

@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone, expected_solar_azimuth, against_unit",
    test_cases,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_azimuth_pvlib(
    longitude,
    latitude,
    timestamp,
    timezone,
    expected_solar_azimuth,
    against_unit,
    tolerance,
):
    calculated_solar_azimuth = calculate_solar_azimuth_pvlib(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
    )

    # Check types
    assert isinstance(calculated_solar_azimuth, SolarAzimuth)

    # Assert output
    assert pytest.approx(
        getattr(expected_solar_azimuth, against_unit), tolerance) == getattr(calculated_solar_azimuth, against_unit)

    # Assert range

