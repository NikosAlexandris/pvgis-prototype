import pytest
from pvgisprototype.api.geometry.hour_angle import calculate_hour_angle
from .helpers import read_noaa_spreadsheet, test_cases_from_data
from pvgisprototype.constants import SOLAR_TIME_NAME, HOUR_ANGLE_NAME, DEGREES
from pvgisprototype import SolarHourAngle
from datetime import datetime


test_cases_data = read_noaa_spreadsheet(
    './tests/data/test_cases_noaa_spreadsheet.xlsx'
)
test_cases = test_cases_from_data(
    test_cases_data,
    against_unit=DEGREES,
    timestamp='timestamp',
    true_solar_time_in_minutes=SOLAR_TIME_NAME,
    solar_hour_angle=HOUR_ANGLE_NAME,
)
tolerances = [0.1]

@pytest.mark.parametrize(
    "date, true_solar_time_in_minutes, expected_hour_angle, against_unit", test_cases,
)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_hour_angle(
    date,
    true_solar_time_in_minutes,
    expected_hour_angle,
    against_unit,
    tolerance,
):
    total_seconds = true_solar_time_in_minutes[0] * 60
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    true_solar_time_as_datetime = datetime(
        year=date.year,
        month=date.month,
        day=date.day,
        hour=int(hours),
        minute=int(minutes),
        second=int(seconds),
        )
    
    calculated_hour_angle = calculate_hour_angle(
        solar_time=true_solar_time_as_datetime
    )

    # Check types
    assert isinstance(calculated_hour_angle, SolarHourAngle)

    # Assert output
    assert pytest.approx(getattr(expected_hour_angle, against_unit), tolerance) == getattr(
        calculated_hour_angle, against_unit)
