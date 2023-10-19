import pytest
from pvgisprototype.api.geometry.solar_position import model_solar_geometry_overview
from pvgisprototype.api.geometry.models import SolarTimeModels, SolarPositionModels
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype import SolarDeclination
from pvgisprototype import SolarHourAngle
from pvgisprototype import SolarZenith
from pvgisprototype import SolarAltitude
from pvgisprototype import SolarAzimuth
from pvgisprototype.constants import (
    ALTITUDE_NAME,
    AZIMUTH_NAME,
    DECLINATION_NAME,
    HOUR_ANGLE_NAME,
    ZENITH_NAME,
    RADIANS,
)


test_cases_data = read_noaa_spreadsheet(
    './tests/data/test_cases_noaa_spreadsheet.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit=RADIANS,
    longitude='longitude',
    latitude='latitude',
    timestamp='timestamp',
    timezone='timezone',
    declination=DECLINATION_NAME,
    hour_angle=HOUR_ANGLE_NAME,
    zenith=ZENITH_NAME,
    altitude=ALTITUDE_NAME,
    azimuth=AZIMUTH_NAME,
)

tolerances = [0.1]      # 1, 0.5, 

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
    expected_declination, expected_hour_angle, expected_zenith, expected_altitude,\
    expected_azimuth, against_unit", test_cases,
)
@pytest.mark.parametrize('solar_time_model', solar_time_models)
@pytest.mark.parametrize('solar_position_model', solar_position_models)
@pytest.mark.parametrize('tolerance', tolerances)
def test_model_solar_geometry_overview(
    longitude,
    latitude,
    timestamp,
    timezone,
    expected_declination,
    expected_hour_angle,
    expected_zenith,
    expected_altitude,
    expected_azimuth,
    against_unit,
    solar_position_model,
    solar_time_model,
    tolerance,
):
    calculated_solar_declination, calculated_solar_hour_angle, calculated_solar_zenith, calculated_solar_altitude, calculated_solar_azimuth = model_solar_geometry_overview(
        longitude = longitude,
        latitude = latitude,
        timestamp = timestamp,
        timezone = timezone,
        solar_position_model = solar_position_model,
        solar_time_model = solar_time_model,
    )

    # Check types
    assert calculated_solar_declination is None or isinstance(calculated_solar_declination, SolarDeclination)
    assert calculated_solar_hour_angle is None or  isinstance(calculated_solar_hour_angle, SolarHourAngle)
    assert isinstance(calculated_solar_zenith, SolarZenith)
    assert isinstance(calculated_solar_altitude, SolarAltitude)
    assert isinstance(calculated_solar_azimuth, SolarAzimuth)

    # Assert output
    assert calculated_solar_declination is None or pytest.approx(
        getattr(expected_declination, against_unit), tolerance) == getattr(calculated_solar_declination, against_unit)
    
    assert calculated_solar_hour_angle is None or pytest.approx(
        getattr(expected_hour_angle, against_unit), tolerance) == getattr(calculated_solar_hour_angle, against_unit)

    assert pytest.approx(
        getattr(expected_zenith, against_unit), tolerance) == getattr(calculated_solar_zenith, against_unit)

    assert pytest.approx(
        getattr(expected_altitude, against_unit), tolerance) == getattr(calculated_solar_altitude, against_unit)
        
    assert pytest.approx(
        getattr(expected_azimuth, against_unit), tolerance) == getattr(calculated_solar_azimuth, against_unit)

