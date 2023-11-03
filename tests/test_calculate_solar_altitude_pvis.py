import pytest
from pvgisprototype import SolarAltitude
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.algorithms.pvis.solar_altitude import calculate_solar_altitude_pvis
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.constants import ALTITUDE_NAME
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR, DEGREES


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
    altitude=ALTITUDE_NAME,
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
    "longitude, latitude, timestamp, timezone, expected_solar_alitude, against_unit",
    test_cases,
)
@pytest.mark.parametrize('model', models)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_altitude_pvis(
    longitude,
    latitude,
    timestamp,
    timezone,
    expected_solar_alitude,
    against_unit,
    model,
    tolerance,
):
    calculated_solar_altitude = calculate_solar_altitude_pvis(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        perigee_offset=PERIGEE_OFFSET,
        eccentricity_correction_factor=ECCENTRICITY_CORRECTION_FACTOR,
        solar_time_model=model,
    )

    # Check types
    assert isinstance(calculated_solar_altitude, SolarAltitude)

    # Assert output
    assert pytest.approx(
        getattr(expected_solar_alitude, against_unit), tolerance) == getattr(calculated_solar_altitude, against_unit)
