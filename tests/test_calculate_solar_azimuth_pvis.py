import pytest
from pvgisprototype import SolarAzimuth
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import AZIMUTH_NAME, DEGREES
from pvgisprototype.algorithms.pvis.solar_azimuth import calculate_solar_azimuth_pvis
from pvgisprototype.api.geometry.models import SolarTimeModels


test_cases_data = read_noaa_spreadsheet(
    './tests/cases/noaa.xlsx'
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

models = [
    # SolarTimeModels.ephem,
    SolarTimeModels.milne,
    SolarTimeModels.noaa,
    # SolarTimeModels.pvgis,
    # SolarTimeModels.skyfield,
]

@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone, expected_solar_azimuth, against_unit",
    test_cases,
)
@pytest.mark.parametrize('model', models)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_azimuth_pvis(
    longitude,
    latitude,
    timestamp,
    timezone,
    expected_solar_azimuth,
    against_unit,
    model,
    tolerance,
):
    calculated_solar_azimuth = calculate_solar_azimuth_pvis(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_time_model=model,
    )

    # Check types
    assert isinstance(calculated_solar_azimuth, SolarAzimuth)

    # Assert output
    assert pytest.approx(
        getattr(expected_solar_azimuth, against_unit), tolerance) == getattr(calculated_solar_azimuth, against_unit)

    # Assert range
