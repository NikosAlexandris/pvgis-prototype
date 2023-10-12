import pytest
from pvgisprototype.algorithms.skyfield.solar_time import calculate_solar_time_skyfield
from datetime import datetime
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import SOLAR_TIME_NAME
from pvgisprototype.api.utilities.timestamp import timestamp_to_minutes


test_cases_data = read_noaa_spreadsheet(
    './tests/data/test_cases_noaa_spreadsheet.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit='minutes',
    longitude='longitude',
    latitude='latitude',
    timestamp='timestamp',
    timezone='timezone',
    solar_time=SOLAR_TIME_NAME,
)

tolerances = [0.1]

@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone, expected_solar_time, against_unit",
    test_cases,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_time_skyfield(
    longitude,
    latitude,
    timestamp,
    timezone,
    expected_solar_time,
    against_unit,
    tolerance,
):
    assert against_unit == expected_solar_time[1] == 'minutes'
    calculated_solar_time = calculate_solar_time_skyfield(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
    )

    calculated_solar_time_in_minutes = timestamp_to_minutes(calculated_solar_time)

    # Check types
    assert isinstance(calculated_solar_time, datetime)

    # Assert output
    assert pytest.approx(expected_solar_time[0], tolerance) == calculated_solar_time_in_minutes

