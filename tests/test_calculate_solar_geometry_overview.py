import pytest
from pvgisprototype.api.geometry.solar_position import calculate_solar_geometry_overview
from pvgisprototype.api.geometry.models import SolarPositionModels
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype import RefractedSolarZenith
from pvgisprototype.constants import (
    POSITION_ALGORITHM_NAME,
    TIME_ALGORITHM_NAME,
    ALTITUDE_NAME,
    AZIMUTH_NAME,
    DECLINATION_NAME,
    HOUR_ANGLE_NAME,
    ZENITH_NAME,
    UNITS_NAME,
)
from pvgisprototype.api.geometry.models import SolarTimeModels


test_cases_data = read_noaa_spreadsheet(
    './tests/data/test_cases_noaa_spreadsheet.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit='degrees',
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
    expected_declination, expected_hour_angle, expected_zenith, expected_altitude,\
    expected_azimuth, against_unit", test_cases,
)
@pytest.mark.parametrize('solar_time_model', solar_time_models)
@pytest.mark.parametrize('solar_position_models', solar_position_models)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_geometry_overview(
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
    solar_time_model,
    solar_position_models,
    tolerance,
):
    calculated = calculate_solar_geometry_overview(
        longitude = longitude,
        latitude = latitude,
        timestamp = timestamp,
        timezone = timezone,  # NOTE: Could also be None or ZoneInfo('UTC'), even if tzinfo in datetime
        angle_output_units = against_unit,
        solar_position_models = solar_position_models,
        solar_time_model = solar_time_model,
    )

    # Check types
    assert isinstance(calculated, list)
    assert len(calculated) == len(solar_position_models)

    for idx in range(len(solar_position_models)):
        assert isinstance(calculated[idx], dict)
        assert isinstance(calculated[idx][POSITION_ALGORITHM_NAME], str)
        assert isinstance(calculated[idx][TIME_ALGORITHM_NAME], str)
        assert DECLINATION_NAME not in calculated[idx] or isinstance(calculated[idx][DECLINATION_NAME], float)
        assert HOUR_ANGLE_NAME not in calculated[idx] or isinstance(calculated[idx][HOUR_ANGLE_NAME], float)
        assert isinstance(calculated[idx][ZENITH_NAME], float)
        assert isinstance(calculated[idx][ALTITUDE_NAME], float)
        assert isinstance(calculated[idx][AZIMUTH_NAME], float)
        assert isinstance(calculated[idx][UNITS_NAME], str)

        # Assert output
        assert DECLINATION_NAME not in calculated[idx] or pytest.approx(
            getattr(expected_declination, against_unit), tolerance) == calculated[idx][DECLINATION_NAME]

        assert HOUR_ANGLE_NAME not in calculated[idx] or pytest.approx(
            getattr(expected_hour_angle, against_unit), tolerance) == calculated[idx][HOUR_ANGLE_NAME]

        assert pytest.approx(
            getattr(expected_zenith, against_unit), tolerance) == calculated[idx][ZENITH_NAME]

        assert pytest.approx(
            getattr(expected_altitude, against_unit), tolerance) == calculated[idx][ALTITUDE_NAME]

        assert pytest.approx(
            getattr(expected_azimuth, against_unit), tolerance) == calculated[idx][AZIMUTH_NAME]

