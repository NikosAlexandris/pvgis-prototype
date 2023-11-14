import pytest
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from pvgisprototype.api.utilities.conversions import convert_float_to_radians_if_requested
from pvgisprototype.algorithms.noaa.time_offset import calculate_time_offset_noaa
from pvgisprototype.algorithms.noaa.time_offset import calculate_time_offset_time_series_noaa
from math import pi
from math import radians
from zoneinfo import ZoneInfo
import numpy as np
from pvgisprototype.constants import RADIANS


test_cases = [
    (  0.0, datetime(2023, 7, 25, 12),  ZoneInfo('UTC'), "minutes", RADIANS,    0.0, 'minutes'),
    ( 90.0, datetime(2023, 12, 21, 12), ZoneInfo('UTC'), "minutes", RADIANS,  360.0, 'minutes'),
    (-90.0, datetime(2023, 1, 1, 12),   ZoneInfo('UTC'), "minutes", RADIANS, -360.0, 'minutes'),
    (  0.0, datetime(2023, 6, 21, 12),  ZoneInfo('UTC'), "minutes", RADIANS, -120.0, 'minutes'),
]
tolerances = [10, 5, 1, 0.1]


@pytest.mark.parametrize("longitude, timestamp, timezone, time_output_units, angle_units, expected, expected_unit", test_cases)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_time_offset_noaa(
    longitude: float,
    timestamp: datetime,
    timezone: ZoneInfo,
    time_output_units: str,
    angle_units: str,
    expected: float,
    expected_unit: str,
    tolerance: float,
):
    longitude = convert_float_to_radians_if_requested(longitude, 'radians')
    time_offset = calculate_time_offset_noaa(
        longitude=longitude,
        timestamp=timestamp,
        timezone=timezone,
        # time_output_units=time_output_units,
    )
    expected_unit == time_output_units
    assert pytest.approx(expected, tolerance) == time_offset.value
    assert expected_unit == time_offset.unit


# cases = [
#     ( 30, [datetime(2023, 12, 21, 12)],
#                                         ZoneInfo('UTC'),                  -6.54, 'minutes'),
#     ( 30, [datetime(2023, 12, 21, 12)], 
#                                         ZoneInfo('Europe/Athens'),        -6.54, 'minutes'),
#     ( 30, [datetime(2023, 12, 21, 12)], 
#                                         ZoneInfo('America/Los_Angeles'), 362.17, 'minutes'),
#     (-30, [datetime(2023, 7, 25, 12), datetime(2023, 7, 26, 12)],
#                                         ZoneInfo('UTC'),            [20, -6.55], 'minutes'),
#     (-30, [datetime(2023, 7, 25, 12), datetime(2023, 7, 26, 12)],
#                                         ZoneInfo('UTC'),            [21, -6.55], 'minutes'),
# ]
cases = [
    ( 0, [datetime(2023, 3, 21, 12)],  ZoneInfo('UTC'),   [0], 'minutes'),  # Equinox, expect near zero offset
    ( 0, [datetime(2023, 6, 21, 12)],  ZoneInfo('UTC'), [-15], 'minutes'),  # Summer solstice, expect -15 minutes
    ( 0, [datetime(2023, 12, 21, 12)], ZoneInfo('UTC'),  [15], 'minutes'),  # Winter solstice, expect +15 minutes
    (45, [datetime(2023, 3, 21, 12)],  ZoneInfo('UTC'), [180], 'minutes'),  # Equinox at 45 degrees longitude, expect 180 minutes or 3 hours
    (45, [datetime(2023, 3, 21, 12)],  ZoneInfo('UTC'), [174], 'minutes'),  # Equinox at 45 degrees longitude, expect 180 minutes or 3 hours
    (45, [datetime(2023, 3, 21, 12)],  ZoneInfo('UTC'), [172], 'minutes'),  # Equinox at 45 degrees longitude, expect 180 minutes or 3 hours
    (45, [datetime(2023, 3, 21, 12)],  ZoneInfo('UTC'), [170], 'minutes'),  # Equinox at 45 degrees longitude, expect 180 minutes or 3 hours
]
@pytest.mark.parametrize("longitude, timestamps, timezone, expected, expected_unit", cases)
@pytest.mark.parametrize('tolerance', tolerances)
def test_calculate_time_offset_time_series_noaa(
    longitude,
    timestamps, 
    timezone,
    expected,
    expected_unit,
    tolerance,
):
    longitude = convert_float_to_radians_if_requested(longitude, 'radians')
    calculated = calculate_time_offset_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        time_output_units=expected_unit,
    )
    # calculated_values = np.array([item.value for item in calculated])
    calculated_values = np.array([item.value for item in calculated])
    expected = np.atleast_1d(np.array(expected))
    assert np.allclose(expected, calculated_values, atol=tolerance)
    calculated_units = np.array([item.unit for item in calculated])
    assert np.all(expected_unit == calculated_units)
