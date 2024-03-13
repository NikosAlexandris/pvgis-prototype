
import pytest
from pvgisprototype.api.geometry.declination import model_solar_declination
from pvgisprototype.api.geometry.models import SolarDeclinationModel
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import DECLINATION_NAME, DEGREES
from pvgisprototype import SolarDeclination


test_cases_data = read_noaa_spreadsheet(
    './tests/cases/noaa.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit=DEGREES,
    timestamp='timestamp',
    timezone='timezone',
    declination=DECLINATION_NAME,
)
tolerances = [0.1]

declination_models = [
    SolarDeclinationModel.hargreaves,
    SolarDeclinationModel.noaa,
    SolarDeclinationModel.pvis,
    SolarDeclinationModel.pvlib,
]

@pytest.mark.parametrize(
    "timestamp, timezone,\
    expected_solar_declination, against_unit", test_cases,
)
@pytest.mark.parametrize('declination_model', declination_models)
@pytest.mark.parametrize('tolerance', tolerances)
def test_model_solar_declination(
    timestamp,
    timezone,
    expected_solar_declination,
    against_unit,
    declination_model,
    tolerance,
):
    calculated_solar_declination = model_solar_declination(
        timestamp=timestamp,
        timezone=timezone,
        declination_model=declination_model,
    )

    # Check types
    assert isinstance(calculated_solar_declination, SolarDeclination)

    # Assert output
    assert pytest.approx(
        getattr(expected_solar_declination, against_unit), tolerance) == getattr(
            calculated_solar_declination, against_unit)
