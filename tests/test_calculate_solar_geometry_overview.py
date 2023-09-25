import pytest
from pvgisprototype.api.geometry.solar_position import calculate_solar_geometry_overview
from pvgisprototype.api.geometry.models import SolarPositionModels
from .helpers import load_test_cases
from pvgisprototype import RefractedSolarZenith


test_cases = load_test_cases(
    '/mnt/c/Users/olygo/Documents/projects/JRC/PVGIS/modernize/test_cases/Test_cases_extracted_from_NOAA_Solar_Calculator_copy.xlsx'
)

tolerances = [1, 0.5, 0.1]

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
        assert isinstance(calculated[idx]['Model'], str)
        assert 'Declination' not in calculated[idx] or isinstance(calculated[idx]['Declination'], float)
        assert 'Hour Angle' not in calculated[idx] or isinstance(calculated[idx]['Hour Angle'], float)
        assert isinstance(calculated[idx]['Zenith'], float)
        assert isinstance(calculated[idx]['Altitude'], float)
        assert isinstance(calculated[idx]['Azimuth'], float)
        assert isinstance(calculated[idx]['Units'], str)

        # Assert output
        assert 'Declination' not in calculated[idx] or calculated[idx]['Declination'] == pytest.approx(
            getattr(expected_declination, angle_output_units),
            tolerance,
            )
        assert calculated[idx]['Altitude'] == pytest.approx(
            getattr(expected_altitude, angle_output_units),
            tolerance,
            )
        
        if calculated[idx]['Model'] == 'NOAA':          # FIXME: Remove this when noaa-azimuth is fixed
            continue

        assert calculated[idx]['Azimuth'] == pytest.approx(
            getattr(expected_azimuth, angle_output_units),
            tolerance,
            )

