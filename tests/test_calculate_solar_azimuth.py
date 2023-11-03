import pytest
from pvgisprototype.api.geometry.azimuth import calculate_solar_azimuth
from pvgisprototype.api.geometry.models import SolarTimeModels, SolarPositionModels
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import AZIMUTH_NAME, TIME_ALGORITHM_NAME, POSITION_ALGORITHM_NAME, UNITS_NAME, DEGREES


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

# FIXME: The combinations of the timing/position models are repeated
solar_time_models = [
    # SolarTimeModels.ephem,
    SolarTimeModels.milne,
    SolarTimeModels.noaa,
    # SolarTimeModels.pvgis,
    # SolarTimeModels.skyfield,
]
solar_position_models = [[
    SolarPositionModels.noaa,
    SolarPositionModels.pvis,
    SolarPositionModels.pvlib,
    SolarPositionModels.pysolar,
    SolarPositionModels.skyfield,
    SolarPositionModels.suncalc,
]]

@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone,\
    expected_azimuth, against_unit", test_cases,
)
@pytest.mark.parametrize('solar_time_model', solar_time_models)
@pytest.mark.parametrize('solar_position_models', solar_position_models)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_azimuth(
    longitude,
    latitude,
    timestamp,
    timezone,
    expected_azimuth,
    against_unit,
    solar_position_models,
    solar_time_model,
    tolerance,
):
    calculated = calculate_solar_azimuth(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_position_models=solar_position_models,
        solar_time_model=solar_time_model,
        angle_output_units=against_unit,
    )

    # Check types
    assert isinstance(calculated, list)

    # Assert output
    for idx in range(len(calculated)):
        assert isinstance(calculated[idx], dict)
        assert isinstance(calculated[idx][TIME_ALGORITHM_NAME], str)
        assert isinstance(calculated[idx][POSITION_ALGORITHM_NAME], str)
        assert isinstance(calculated[idx][AZIMUTH_NAME], float)
        assert isinstance(calculated[idx][UNITS_NAME], str)

        assert pytest.approx(
            getattr(expected_azimuth, against_unit), tolerance) == calculated[idx][AZIMUTH_NAME]
