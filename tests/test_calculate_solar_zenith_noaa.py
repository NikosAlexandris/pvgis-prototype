import pytest
from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_noaa
from pvgisprototype import SolarZenith
# from pvgisprototype.algorithms.noaa.solar_zenith import adjust_solar_zenith_for_atmospheric_refraction
# from pvgisprototype.algorithms.noaa.solar_zenith import adjust_solar_zenith_for_atmospheric_refraction_time_series
# from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import ZENITH_NAME, HOUR_ANGLE_NAME, DEGREES


test_cases_data = read_noaa_spreadsheet(
    './tests/cases/noaa.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit=DEGREES,
    latitude='latitude',
    timestamp='timestamp',
    hour_angle=HOUR_ANGLE_NAME,
    zenith=ZENITH_NAME,
)

tolerances = [0.1]

@pytest.mark.parametrize(
    "latitude, timestamp, solar_hour_angle, expected_solar_zenith, against_unit",
    test_cases,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_zenith_noaa(
    latitude,
    timestamp,
    solar_hour_angle,
    expected_solar_zenith,
    against_unit,
    tolerance,
):
    calculated_solar_zenith = calculate_solar_zenith_noaa(
        latitude=latitude,
        timestamp=timestamp,
        solar_hour_angle=solar_hour_angle,
    )

    # Check types
    assert isinstance(calculated_solar_zenith, SolarZenith)

    # Assert output
    assert pytest.approx(
        getattr(expected_solar_zenith, against_unit), tolerance) == getattr(calculated_solar_zenith, against_unit)

    # Assert range








# refraction_flags = [
#         True,
#         False,
# ]
# @pytest.mark.parametrize('refraction_flag', refraction_flags)
# def test_calculate_solar_zenith_noaa(refraction_flag):
#     latitude = Latitude(value=0.5, unit='radians')
#     timestamp = datetime(year=2023, month=8, day=25)
#     solar_hour_angle = SolarHourAngle(value=0.2, unit=RADIANS)
#     result = calculate_solar_zenith_noaa(
#         latitude,
#         timestamp,
#         solar_hour_angle,
#         apply_atmospheric_refraction=refraction_flag
#     )
#     assert isinstance(result, SolarZenith)


# def test_calculate_solar_zenith_noaa_invalid_input():
#     latitude = Latitude(value=0.5, unit='radians')
#     timestamp = datetime(2023, 8, 25)
#     solar_hour_angle = SolarHourAngle(value=0.2, unit='radians')
#     with pytest.raises(ValueError):
#         calculate_solar_zenith_noaa(latitude, timestamp, solar_hour_angle)


# solar_zenith_values = [
#         0.5,
# ]
# @pytest.mark.parametrize('solar_zenith', solar_zenith_values)
# def test_adjust_solar_zenith_for_atmospheric_refraction_typical_case(solar_zenith):
#     calculated_refracted_solar_zenith = adjust_solar_zenith_for_atmospheric_refraction(solar_zenith)
#     assert isinstance(calculated_refracted_solar_zenith, SolarZenith)


# minimum_solar_zenith = 0
# maximum_solar_zenith = pi + 0.0146
# solar_zenith_invalid_values = [
#         minimum_solar_zenith - random(),  # less than minimum
#         minimum_solar_zenith - random(),
#         minimum_solar_zenith - random(),
#         maximum_solar_zenith + random(),  # more than maximum
#         maximum_solar_zenith + random(),
#         maximum_solar_zenith + random(),
# ]
# @pytest.mark.parametrize('solar_zenith', solar_zenith_invalid_values)
# def test_adjust_solar_zenith_for_atmospheric_refraction_invalid_input(solar_zenith):
#     with pytest.raises(ValueError):
#         adjust_solar_zenith_for_atmospheric_refraction(solar_zenith)


# def test_adjust_solar_zenith_for_atmospheric_refraction_time_series():
#     solar_zenith_series = np.array([0.5, 0.6, 0.7])  # radians
#     result = adjust_solar_zenith_for_atmospheric_refraction_time_series(
#         solar_zenith_series=solar_zenith_series,
#     )
#     assert isinstance(result, np.ndarray)


# def test_adjust_solar_zenith_for_atmospheric_refraction_time_series_invalid_input():
#     solar_zeniths = np.array([4, 0.6, 0.7])  # Invalid values
#     with pytest.raises(ValueError):
#         adjust_solar_zenith_for_atmospheric_refraction_time_series(solar_zeniths)


# refraction_flags = [
#         True,
#         False,
# ]
# @pytest.mark.parametrize('refraction_flag', refraction_flags)
# def test_calculate_solar_zenith_time_series_noaa(refraction_flag):
#     latitude = Latitude(value=0.5, unit=RADIANS)
#     timestamps = [datetime(2023, 8, 25), datetime(2023, 8, 26)]
#     solar_hour_angle_series = [
#         SolarHourAngle(value=0.2, unit=RADIANS),
#         SolarHourAngle(value=0.3, unit=RADIANS),
#     ]
#     result = calculate_solar_zenith_time_series_noaa(
#         latitude=latitude,
#         timestamps=timestamps,
#         solar_hour_angle_series=solar_hour_angle_series,
#         apply_atmospheric_refraction=refraction_flag,
#     )
#     assert isinstance(result, np.ndarray)


# def test_calculate_solar_zenith_time_series_noaa_invalid_input():
#     # Test with invalid input values
#     latitude = Latitude(value=10, unit=RADIANS)  # out-of-range latitude
#     timestamps = [datetime(2023, 8, 25), datetime(2023, 8, 26)]
#     solar_hour_angle_series = [
#         SolarHourAngle(value=0.2, unit=RADIANS),
#         SolarHourAngle(value=0.3, unit=RADIANS),
#     ]
#     with pytest.raises(ValueError):
#         calculate_solar_zenith_time_series_noaa(
#             latitude, timestamps, solar_hour_angle_series
#         )
