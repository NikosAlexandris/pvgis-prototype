import pytest
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_noaa
# from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
from pvgisprototype import SolarDeclination
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import DECLINATION_NAME


test_cases_data = read_noaa_spreadsheet(
    './tests/data/test_cases_noaa_spreadsheet.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit='radians',
    timestamp='timestamp',
    declination=DECLINATION_NAME,
)

tolerances = [0.1]

@pytest.mark.parametrize(
    "timestamp, expected_solar_declination, against_unit",
    test_cases,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_solar_declination_noaa(
    timestamp,
    against_unit,
    expected_solar_declination,
    tolerance,
):
    calculated_solar_declination = calculate_solar_declination_noaa(
        timestamp=timestamp,
    )

    # Check types
    assert isinstance(calculated_solar_declination, SolarDeclination)

    # Assert output
    assert pytest.approx(
        getattr(expected_solar_declination, against_unit), tolerance) == getattr(calculated_solar_declination, against_unit)

    # Assert range






# tolerances = [1, 0.1, 0.01]


# @pytest.fixture
# def timestamps():
#     return [
#         datetime(year=2023, month=7, day=25, hour=12), 
#         datetime(year=2023, month=12, day=21, hour=12),
#         datetime(year=2023, month=1, day=1, hour=12), 
#         datetime(year=2023, month=6, day=21, hour=12),
#     ]


# @pytest.fixture
# def expected_solar_declinations():
#     return [
#         (0.41, 'radians'),
#         (-0.41, 'radians'),
#         (-0.41, 'radians'),
#         (0.41, 'radians'),
#     ]


# @pytest.mark.parametrize(
#     'timestamp, expected_angle, angle_output_units',
#     [
#         (datetime(2023, 7, 25, 12), 0.41, 'radians'),
#         (datetime(2023, 12, 21, 12), -0.41, 'radians'),
#         (datetime(2023, 1, 1, 12), -0.41, 'radians'),
#         (datetime(2023, 6, 21, 12), 0.41, 'radians'),
#         (datetime(2023, 1, 1), -23.38044, 'degrees'),  # Around vernal equinox
#         (datetime(2023, 3, 20), 0, 'degrees'),  # Around vernal equinox
#         (datetime(2023, 3, 21), 0, 'degrees'),  # Around vernal equinox
#         (datetime(2023, 6, 20), 23.44, 'degrees'),  # Around summer solstice
#         (datetime(2023, 6, 21), 23.44, 'degrees'),  # Around summer solstice
#         (datetime(2023, 9, 22), 0, 'degrees'),  # Around autumnal equinox
#         (datetime(2023, 9, 23), 0, 'degrees'),  # Around autumnal equinox
#         (datetime(2023, 12, 21), -23.44, 'degrees'),  # Around winter solstice
#         (datetime(2023, 12, 22), -23.44, 'degrees'),  # Around winter solstice
#         (datetime(2023, 12, 30), -16.428456, 'degrees'),  # Around winter solstice
#     ],
# )
# @pytest.mark.parametrize('tolerance', tolerances)
# def test_calculate_solar_declination_noaa(
#     timestamp: datetime,
#     expected_angle: float,
#     angle_output_units: str,
#     tolerance: float,
# ):
#     calculated_solar_declination = calculate_solar_declination_noaa(timestamp, angle_output_units)
#     assert angle_output_units == calculated_solar_declination.unit
#     assert pytest.approx(expected_angle, tolerance) == calculated_solar_declination.value


# def test_calculate_solar_declination_noaa_invalid_input():
#     # test an incorrect type of input
#     with pytest.raises(pydantic.ValidationError):
#         calculate_solar_declination_noaa("not a datetime object")

#     # test an incorrect value of angle_output_units
#     with pytest.raises(pydantic.ValidationError):
#         calculate_solar_declination_noaa(datetime(year=2023, month=7, day=25, hour=12), angle_output_units="not a valid unit")


# @pytest.mark.parametrize('tolerance', tolerances)
# def test_calculate_solar_declination_time_series_noaa(
#     timestamps,
#     expected_solar_declinations,
#     tolerance,
# ):
#     calculated_solar_declinations = calculate_solar_declination_time_series_noaa(timestamps)
#     assert isinstance(calculated_solar_declinations, np.ndarray)
#     assert all(isinstance(item, SolarDeclination) for item in calculated_solar_declinations)

#     expected_values, expected_units = zip(*expected_solar_declinations)
#     assert np.allclose(expected_values, [item.value for item in calculated_solar_declinations], atol=tolerance)
#     assert all(expected_unit == calculated.unit for expected_unit, calculated in zip(expected_units, calculated_solar_declinations))
