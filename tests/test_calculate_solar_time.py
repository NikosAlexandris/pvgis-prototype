

import pytest
from pvgisprototype.api.geometry.solar_time import calculate_solar_time
from pvgisprototype.api.geometry.models import SolarTimeModels
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import SOLAR_TIME_NAME, TIME_ALGORITHM_NAME, UNITS_NAME
from datetime import datetime
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

solar_time_models = [[
    # SolarTimeModels.ephem,
    SolarTimeModels.milne,
    SolarTimeModels.noaa,
    # SolarTimeModels.pvgis,
    # SolarTimeModels.skyfield,
]]

@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone,\
    expected_solar_time_in_minutes, against_unit", test_cases,
)
@pytest.mark.parametrize('solar_time_models', solar_time_models)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_time(
    longitude,
    latitude,
    timestamp,
    timezone,
    expected_solar_time_in_minutes,
    against_unit,
    solar_time_models,
    tolerance,
):
    assert expected_solar_time_in_minutes[1] == against_unit
    calculated = calculate_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_time_models=solar_time_models,
        time_output_units=against_unit,
    )

    # Check types
    assert isinstance(calculated, list)

    # Assert output
    for idx in range(len(calculated)):
        assert isinstance(calculated[idx], dict)
        assert isinstance(calculated[idx][TIME_ALGORITHM_NAME], str)
        assert isinstance(calculated[idx][SOLAR_TIME_NAME], datetime)
        assert isinstance(calculated[idx][UNITS_NAME], str)

        calculated_solar_time_in_minutes = timestamp_to_minutes(calculated[idx][SOLAR_TIME_NAME])
        assert pytest.approx(expected_solar_time_in_minutes[0], tolerance) == calculated_solar_time_in_minutes
