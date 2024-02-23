import pytest
from pvgisprototype.api.geometry.solar_time import model_solar_time
from pvgisprototype.api.geometry.models import SolarTimeModel
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.api.utilities.timestamp import timestamp_to_minutes
from datetime import datetime
from pvgisprototype.constants import SOLAR_TIME_NAME


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
tolerances = [0.1]      # 1, 0.5, 

solar_time_models = [
    # SolarTimeModel.ephem,
    SolarTimeModel.milne,
    SolarTimeModel.noaa,
    # SolarTimeModel.pvgis,
    # SolarTimeModel.skyfield,
]

@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone,\
    expected_solar_time, against_unit", test_cases,
)
@pytest.mark.parametrize('solar_time_model', solar_time_models)
@pytest.mark.parametrize('tolerance', tolerances)
def test_model_solar_time(
    longitude,
    latitude,
    timestamp,
    timezone,
    expected_solar_time,
    against_unit,
    solar_time_model,
    tolerance,
):
    assert against_unit == expected_solar_time[1] == 'minutes'
    calculated_solar_time = model_solar_time(
        longitude=longitude,  
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_time_model=solar_time_model,
    )

    calculated_solar_time_in_minutes = timestamp_to_minutes(calculated_solar_time)

    # Check types
    assert isinstance(calculated_solar_time, datetime)

    # Assert output      
    assert pytest.approx(expected_solar_time[0], tolerance) == calculated_solar_time_in_minutes

