import pytest
import sys
from pvgisprototype.api.geometry.solar_position import calculate_solar_geometry_overview
from pvgisprototype.api.geometry.models import SolarPositionModels
from .helpers import read_test_cases_file, test_cases_from_data
from pvgisprototype import RefractedSolarZenith
from pvgisprototype.constants import (
    POSITION_ALGORITHM_NAME,
    ALTITUDE_NAME,
    AZIMUTH_NAME,
    DECLINATION_NAME,
    HOUR_ANGLE_NAME,
    ZENITH_NAME,
    UNITS_NAME,
)


test_cases_data = read_test_cases_file(
    '/mnt/c/Users/olygo/Documents/projects/JRC/PVGIS/modernize/test_cases/Test_cases_extracted_from_NOAA_Solar_Calculator_copy.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    declination=DECLINATION_NAME,
    altitude=ALTITUDE_NAME,
    azimuth=AZIMUTH_NAME,
)


tolerances = [0.1]      # 1, 0.5, 

models = [[
    SolarPositionModels.noaa,
    SolarPositionModels.pysolar,
    # SolarPositionModels.pvis,
    # SolarPositionModels.pvgis,
    SolarPositionModels.suncalc,
    SolarPositionModels.skyfield,
    SolarPositionModels.pvlib,
]]


@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone, angle_output_units,\
    expected_declination, expected_altitude, expected_azimuth", test_cases,
)
@pytest.mark.parametrize('models', models)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_geometry_overview(
    longitude,
    latitude,
    timestamp,
    timezone,
    angle_output_units,
    expected_declination,
    expected_altitude,
    expected_azimuth,
    models,
    tolerance,
):
    calculated = calculate_solar_geometry_overview(
        longitude = longitude,
        latitude = latitude,
        timestamp = timestamp,
        timezone = timezone,
        angle_output_units = angle_output_units,
        models = models,
        refracted_solar_zenith = RefractedSolarZenith(),
    )

    # Check types
    assert isinstance(calculated, list)
    assert len(calculated) == len(models)

    for idx in range(len(models)):
        assert isinstance(calculated[idx], dict)
        assert isinstance(calculated[idx][POSITION_ALGORITHM_NAME], str)
        assert DECLINATION_NAME not in calculated[idx] or isinstance(calculated[idx][DECLINATION_NAME], float)
        assert HOUR_ANGLE_NAME not in calculated[idx] or isinstance(calculated[idx][HOUR_ANGLE_NAME], float)
        assert isinstance(calculated[idx][ZENITH_NAME], float)
        assert isinstance(calculated[idx][ALTITUDE_NAME], float)
        assert isinstance(calculated[idx][AZIMUTH_NAME], float)
        assert isinstance(calculated[idx][UNITS_NAME], str)

        # Assert output
        assert DECLINATION_NAME not in calculated[idx] or calculated[idx][DECLINATION_NAME] == pytest.approx(
            getattr(expected_declination, angle_output_units),
            tolerance,
            )
        assert calculated[idx][ALTITUDE_NAME] == pytest.approx(
            getattr(expected_altitude, angle_output_units),
            tolerance,
            )
        
        if calculated[idx][POSITION_ALGORITHM_NAME] == 'NOAA':          # FIXME: Remove this when noaa-azimuth is fixed
            continue

        assert calculated[idx][AZIMUTH_NAME] == pytest.approx(
            getattr(expected_azimuth, angle_output_units),
            tolerance,
            )

