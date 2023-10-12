from typing import Literal
import pandas as pd
from zoneinfo import ZoneInfo
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
)
import sys
import os
from timezonefinder import TimezoneFinder



def read_test_cases_file(
        cases_absolute_filepath:str,
    ) -> pd.DataFrame:
    """Read a flat file that contains the test cases, created by NOAA Solar Calculator.
    The first two lines are skipped, and the third is the header. The empty lines are
    removed.

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
        skiprows = [0, 1],
        header = 0,
        engine='openpyxl',
    ).dropna(how='all')
    return test_cases_data


def test_cases_from_data(
        test_cases_data:pd.DataFrame,
        against_unit:Literal['radians', 'degrees'] = 'radians',
        **kwargs,
    ) -> list:
    """Returns test cases (expected values for certain location and datetime) for the
    quantities specified in kwargs. The order in which the kwargs are given is also
    the order in which they will be returned for a test case.

    Parameters
    ----------
    test_cases_data : pd.DataFrame
        Contains test cases created by NOAA Solar Calculator. Has specific field names
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
    test_cases_data = read_test_cases_file(noaa_test_cases_filepath)
    test_cases = test_cases_from_data(
        test_cases_data,
        declination=DECLINATION_NAME,
        altitude=ALTITUDE_NAME,
        azimuth=AZIMUTH_NAME,
    )
    """

    if against_unit not in ['radians', 'degrees']:
        raise ValueError("Invalid value for against_unit. Must be 'radians' or 'degrees'")

    map_field_name = {
        'Longitude':'Longitude',
        'Latitude':'Latitude',
        'Timezone':'Time Zone',
        'UTC_Offset':'UTC_Offset',
        'Timestamp':{
            'Year':'Year',
            'Month':'Month',
            'Day':'Day',
            'Minutes':'Minutes',
            'Seconds':'Seconds',
            'Microseconds':'Microseconds',
        },
        'TimeEquation':'Equation of Time (min)',
        DECLINATION_NAME:'Solar Declination (in °)',
        'SolarNoon':'Solar Noon (hh:mm:ss)',
        'ApparentSunrise':'Apparent Sunrise (hh:mm)',
        'ApparentSunset':'Apparent Sunset (hh:mm)',
        AZIMUTH_NAME:'Azimuth (in °) at Local Time',
        ALTITUDE_NAME:'Elevation (in °) at Local Time',
    }
        
    quantities_to_test = list(kwargs.values())

    test_cases = []
    for _, row in test_cases_data.iterrows():
        selected_data = [
            Longitude(value=row[map_field_name['Longitude']], unit='degrees'),
            Latitude(value=row[map_field_name['Latitude']], unit='degrees'),
            datetime(
                int(row[map_field_name['Timestamp']['Year']]),
                int(row[map_field_name['Timestamp']['Month']]),
                int(row[map_field_name['Timestamp']['Day']]),
                int(row[map_field_name['Timestamp']['Minutes']]),
                int(row[map_field_name['Timestamp']['Seconds']]),
                int(row[map_field_name['Timestamp']['Microseconds']]),
                tzinfo=ZoneInfo(row[map_field_name['Timezone']]),
            ),
            ZoneInfo(row[map_field_name['Timezone']]),
            against_unit,
        ]

        if DECLINATION_NAME in quantities_to_test:
            selected_data.append(
                SolarDeclination(value=row[map_field_name[DECLINATION_NAME]], unit='degrees')
            )
        if ALTITUDE_NAME in quantities_to_test:
            selected_data.append(
                SolarAltitude(value=row[map_field_name[ALTITUDE_NAME]], unit='degrees')
            )
        if AZIMUTH_NAME in quantities_to_test:
            selected_data.append(
                SolarAzimuth(value=row[map_field_name[AZIMUTH_NAME]], unit='degrees')
            )

        test_cases.append(tuple(selected_data))
    return test_cases

