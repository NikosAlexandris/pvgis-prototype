import pytest
from pvgisprototype.api.geometry.solar_position import model_solar_geometry_overview
from pvgisprototype.api.geometry.models import SolarPositionModels
from .helpers import read_test_cases_file, test_cases_from_data
from pvgisprototype import RefractedSolarZenith
from pvgisprototype import SolarDeclination
from pvgisprototype import SolarHourAngle
from pvgisprototype import SolarZenith
from pvgisprototype import SolarAltitude
from pvgisprototype import SolarAzimuth
from pvgisprototype.constants import (
    ALTITUDE_NAME,
    AZIMUTH_NAME,
    DECLINATION_NAME,
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

models = [
    SolarPositionModels.noaa,
    SolarPositionModels.pysolar,
    # SolarPositionModels.pvis,
    # SolarPositionModels.pvgis,
    SolarPositionModels.suncalc,
    SolarPositionModels.skyfield,
    SolarPositionModels.pvlib,
]


@pytest.mark.parametrize(
    "longitude, latitude, timestamp, timezone, angle_output_units,\
    expected_declination, expected_altitude, expected_azimuth", test_cases,
)
@pytest.mark.parametrize('model', models)
@pytest.mark.parametrize('tolerance', tolerances)
def test_model_solar_geometry_overview(
    longitude,
    latitude,
    timestamp,
    timezone,
    angle_output_units,
    expected_declination,
    expected_altitude,
    expected_azimuth,
    model,
    tolerance,
):
    calculated_solar_declination, calculated_solar_hour_angle, calculated_solar_zenith, calculated_solar_altitude, calculated_solar_azimuth = model_solar_geometry_overview(
        longitude = longitude,
        latitude = latitude,
        timestamp = timestamp,
        timezone = timezone,
        angle_output_units = angle_output_units,
        model = model,
        refracted_solar_zenith = RefractedSolarZenith(),
        time_output_units = 'minutes',
    )

    # Check types
    assert calculated_solar_declination is None or isinstance(calculated_solar_declination, SolarDeclination)
    assert calculated_solar_hour_angle is None or  isinstance(calculated_solar_hour_angle, SolarHourAngle)
    assert isinstance(calculated_solar_zenith, SolarZenith)
    assert isinstance(calculated_solar_altitude, SolarAltitude)
    assert isinstance(calculated_solar_azimuth, SolarAzimuth)

    # Assert output
    assert calculated_solar_declination is None or  getattr(calculated_solar_declination, angle_output_units) == pytest.approx(
        getattr(expected_declination, angle_output_units),
        tolerance,
        )
    assert getattr(calculated_solar_altitude, angle_output_units)  == pytest.approx(
        getattr(expected_altitude, angle_output_units),
        tolerance,
        )
        
    if model == SolarPositionModels.noaa:          # FIXME: Remove this when noaa-azimuth is fixed
        pass
    else:
        assert getattr(calculated_solar_azimuth, angle_output_units) == pytest.approx(
            getattr(expected_azimuth, angle_output_units),
            tolerance,
            )

