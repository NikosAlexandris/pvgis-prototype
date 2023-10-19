import pytest
from pvgisprototype.api.geometry.solar_azimuth import model_solar_azimuth
from pvgisprototype.api.geometry.models import SolarTimeModels, SolarPositionModels
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import AZIMUTH_NAME, DEGREES
from pvgisprototype import SolarAzimuth


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
solar_position_models = [
    SolarPositionModels.noaa,
    SolarPositionModels.pvis,
    SolarPositionModels.pvlib,
    SolarPositionModels.pysolar,
    SolarPositionModels.skyfield,
    SolarPositionModels.suncalc,
]

@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone,\
    expected_solar_azimuth, against_unit", test_cases,
)
@pytest.mark.parametrize('solar_time_model', solar_time_models)
@pytest.mark.parametrize('solar_position_model', solar_position_models)
@pytest.mark.parametrize('tolerance', tolerances)
def test_model_solar_azimuth(
    longitude,
    latitude,
    timestamp,
    timezone,
    expected_solar_azimuth,
    against_unit,
    solar_position_model,
    solar_time_model,
    tolerance,
):
    calculated_solar_azimuth = model_solar_azimuth(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_position_model=solar_position_model,
        solar_time_model=solar_time_model,
    )

    # Check types
    assert isinstance(calculated_solar_azimuth, SolarAzimuth)

    # Assert output
    assert pytest.approx(
        getattr(expected_solar_azimuth, against_unit), tolerance) == getattr(
            calculated_solar_azimuth, against_unit)
