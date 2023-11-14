from typing import Literal
import pandas as pd
from zoneinfo import ZoneInfo
from timezonefinder import TimezoneFinder
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarDeclination
from pvgisprototype import SolarAltitude
from pvgisprototype import SolarAzimuth
from pvgisprototype import SolarHourAngle
from pvgisprototype import SolarZenith
from pvgisprototype import EquationOfTime
from datetime import datetime, timezone, timedelta
from pvgisprototype.constants import (
    DECLINATION_NAME,
    ALTITUDE_NAME,
    AZIMUTH_NAME,
    SOLAR_TIME_NAME,
    HOUR_ANGLE_NAME,
    ZENITH_NAME,
    RADIANS,
    DEGREES,
)


def read_noaa_spreadsheet(
        cases_absolute_filepath:str,
    ) -> pd.DataFrame:
    """Read a flat file that contains the test cases, created by NOAA spreadsheet.
    The empty lines are removed.

    Parameters
    ----------
    cases_absolute_filepath : str
        Absolute path of file to read.

    Returns
    -------
    pd.DataFrame
        Contains one test case in each row.
    """

    test_cases_data = pd.read_excel(
        cases_absolute_filepath,
        header = 0,
        engine='openpyxl',
    ).dropna(how='all')
    test_cases_data.iloc[:, :4] = test_cases_data.iloc[:, :4].ffill()
    return test_cases_data


def test_cases_from_data(
        test_cases_data:pd.DataFrame,
        against_unit:Literal['radians', 'degrees'] = RADIANS,
        **kwargs,
    ) -> list:
    """Returns test cases (expected values for certain location and datetime) for the
    quantities specified in kwargs. The sequence in which the kwargs are given is the sequence
    of the returned values.

    Parameters
    ----------
    test_cases_data : pd.DataFrame
        Contains test cases created by NOAA spreadsheet. Has specific field names
        which are mapped to constants quantity-names.
    against_unit : Literal[&#39;radians&#39;, &#39;degrees&#39;], optional
        Unit to test against, by default 'radians'

    Returns
    -------
    list
        Test cases, containing info about location, datetime and expected results for
        the specified quantities in kwargs.

    Example
    -------
    test_cases_data = read_noaa_spreadsheet(noaa_test_cases_filepath)
    test_cases = test_cases_from_data(
        test_cases_data,
        declination=DECLINATION_NAME,
        altitude=ALTITUDE_NAME,
        azimuth=AZIMUTH_NAME,
    )
    """

    if against_unit not in [RADIANS, DEGREES, 'minutes']:
        raise ValueError(f"Invalid value for against_unit. Must be {RADIANS}, {DEGREES} or 'minutes'")

    map_field_name = {
        'latitude':'Latitude (+ to N)',
        'longitude':'Longitude (+ to E)',
        'utc_offset':'UTC Offset',
        'date':'Date',
        'time' :'Time (past local midnight)',
        # :'Julian Day',
        # :'Julian Century',
        # :'Geom Mean Long Sun (deg)',
        # :'Geom Mean Anom Sun (deg)',
        # :'Eccent Earth Orbit',
        # :'Sun Eq of Ctr',
        # :'Sun True Long (deg)',
        # :'Sun True Anom (deg)',
        # :'Sun Rad Vector (AUs)',
        # :'Sun App Long (deg)',
        # :'Mean Obliq Ecliptic (deg)',
        # :'Obliq Corr (deg)',
        # :'Sun Rt Ascen (deg)',
        DECLINATION_NAME :'Sun Declin (deg)',
        # :'var y',
        'equation_of_time':'Eq of Time (minutes)',
        # :'HA Sunrise (deg)',
        # :'Solar Noon (LST)',
        # :'Sunrise Time (LST)',
        # :'Sunset Time (LST)',
        # :'Sunlight Duration (minutes)',
        SOLAR_TIME_NAME:'True Solar Time (min)',
        HOUR_ANGLE_NAME:'Hour Angle (deg)',
        ZENITH_NAME:'Solar Zenith Angle (deg)',
        ALTITUDE_NAME:'Solar Elevation Angle (deg)',
        # :'Approx Atmospheric Refraction (deg)',
        # :'Solar Elevation corrected for atm refraction (deg)',
        AZIMUTH_NAME:'Solar Azimuth Angle (deg cw from N)',
    }

    test_cases = []
    for _, row in test_cases_data.iterrows():

        # TODO not working with utc offset -2:30
        utc_offset = timedelta(hours=row[map_field_name['utc_offset']])
        tz = timezone(utc_offset)

        tf = TimezoneFinder()
        iana_time_zone_name = tf.timezone_at(lat=row[map_field_name['latitude']], lng=row[map_field_name['longitude']])
        time_zone = ZoneInfo(iana_time_zone_name)

        dt = datetime(
                    year=row[map_field_name['date']].year,
                    month=row[map_field_name['date']].month,
                    day=row[map_field_name['date']].day,
                    hour=row[map_field_name['time']].hour,
                    minute=row[map_field_name['time']].minute,
                    second=row[map_field_name['time']].second,
                    microsecond=row[map_field_name['time']].microsecond,
                    tzinfo=tz,
                )
        
        single_case = []
        
        for expected_value in list(kwargs.values()):
            if expected_value == 'longitude':
                single_case.append(
                    Longitude(value=row[map_field_name['longitude']], unit=DEGREES),
                )
            elif expected_value == 'latitude':
                single_case.append(
                    Latitude(value=row[map_field_name['latitude']], unit=DEGREES),
                )
            elif expected_value == 'timestamp':
                single_case.append(
                    dt,
                )
            elif expected_value == 'timezone':
                single_case.append(
                    time_zone,
                )
            elif expected_value == DECLINATION_NAME:
                single_case.append(
                    SolarDeclination(value=row[map_field_name[DECLINATION_NAME]], unit=DEGREES)
                )
            elif expected_value == HOUR_ANGLE_NAME:
                single_case.append(
                    SolarHourAngle(value=row[map_field_name[HOUR_ANGLE_NAME]], unit=DEGREES)
                )
            elif expected_value == ZENITH_NAME:
                single_case.append(
                    SolarZenith(value=row[map_field_name[ZENITH_NAME]], unit=DEGREES)
                )
            elif expected_value == ALTITUDE_NAME:
                single_case.append(
                    SolarAltitude(value=row[map_field_name[ALTITUDE_NAME]], unit=DEGREES)
                )
            elif expected_value == AZIMUTH_NAME:
                single_case.append(
                    SolarAzimuth(value=row[map_field_name[AZIMUTH_NAME]], unit=DEGREES)
                )
            elif expected_value == SOLAR_TIME_NAME:
                single_case.append(
                    (row[map_field_name[SOLAR_TIME_NAME]], 'minutes')
                )
            elif expected_value == 'equation_of_time':
                single_case.append(
                    EquationOfTime(value=row[map_field_name['equation_of_time']], unit='minutes')
                )
            else:
                continue
        single_case.append(against_unit)
        test_cases.append(tuple(single_case))
    return test_cases

