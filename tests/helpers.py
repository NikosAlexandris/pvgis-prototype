import os
import pandas as pd
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarDeclination
from pvgisprototype import SolarHourAngle
from pvgisprototype import SolarZenith
from pvgisprototype import SolarAltitude
from pvgisprototype import SolarAzimuth
from pvgisprototype import RefractedSolarZenith
from datetime import datetime
from zoneinfo import ZoneInfo


def load_test_cases(file_absolute_path:str) -> list:
        
    test_cases_data = pd.read_excel(
        file_absolute_path,
        skiprows = 0,
        header = [1, 2],
        engine='openpyxl',
    )
    test_cases_data = test_cases_data.dropna(how='all')

    test_cases = []
    for idx, row in test_cases_data.iterrows():
        test_cases.append(
            (
                Longitude(value=row['Location']['Longitude'], unit='degrees'),
                Latitude(value=row['Location']['Latitude'], unit='degrees'),
                datetime(
                    int(row['Date (Local Time (AM))']['Year']),
                    int(row['Date (Local Time (AM))']['Month']),
                    int(row['Date (Local Time (AM))']['Day']),
                    int(row['Date (Local Time (AM))']['Minutes']),
                    int(row['Date (Local Time (AM))']['Seconds']),
                    int(row['Date (Local Time (AM))']['Microseconds']),
                    tzinfo=ZoneInfo(row['Location']['Time Zone'])
                ),
                ZoneInfo(row['Location']['Time Zone']),
                'degrees',
                SolarDeclination(value=row['Result']['Solar Declination (in °)'], unit='degrees'),
                # SolarHourAngle(value= , unit='degrees'),
                # SolarZenith(value= , unit='degrees'),
                SolarAltitude(value=row['Result']['Elevation (in °) at Local Time'], unit='degrees'),
                SolarAzimuth(value=row['Result']['Azimuth (in °) at Local Time'], unit='degrees'),
            ))
        test_cases.append(
            (
                Longitude(value=row['Location']['Longitude'], unit='degrees'),
                Latitude(value=row['Location']['Latitude'], unit='degrees'),
                datetime(
                    int(row['Date (Local Time (AM))']['Year']),
                    int(row['Date (Local Time (AM))']['Month']),
                    int(row['Date (Local Time (AM))']['Day']),
                    int(row['Date (Local Time (AM))']['Minutes']),
                    int(row['Date (Local Time (AM))']['Seconds']),
                    int(row['Date (Local Time (AM))']['Microseconds']),
                    tzinfo=ZoneInfo(row['Location']['Time Zone'])
                ),
                ZoneInfo(row['Location']['Time Zone']),
                'radians',
                SolarDeclination(value=row['Result']['Solar Declination (in °)'], unit='degrees'),
                SolarAltitude(value=row['Result']['Elevation (in °) at Local Time'], unit='degrees'),
                SolarAzimuth(value=row['Result']['Azimuth (in °) at Local Time'], unit='degrees'),
            )
        )
    return test_cases