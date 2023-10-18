import pytest
from pvgisprototype.algorithms.pvlib.solar_zenith import calculate_solar_zenith_pvlib
from pvgisprototype import SolarZenith
# import matplotlib.pyplot as plt
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import ZENITH_NAME


test_cases_data = read_noaa_spreadsheet(
    './tests/data/test_cases_noaa_spreadsheet.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit='degrees',
    longitude='longitude',
    latitude='latitude',
    timestamp='timestamp',
    timezone='timezone',
    zenith=ZENITH_NAME,
)

tolerances = [0.1]

@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone, expected_solar_zenith, against_unit",
    test_cases,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_zenith_pvlib(
    longitude,
    latitude,
    timestamp,
    timezone,
    expected_solar_zenith,
    against_unit,
    tolerance,
):
    calculated_solar_zenith = calculate_solar_zenith_pvlib(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
    )

    # Check types
    assert isinstance(calculated_solar_zenith, SolarZenith)

    # Assert output
    assert pytest.approx(
        getattr(expected_solar_zenith, against_unit), tolerance) == getattr(calculated_solar_zenith, against_unit)

    # Assert range

