from devtools import debug
from datetime import datetime
from zoneinfo import ZoneInfo
from math import isfinite
import pvlib
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarAltitudePVLIBInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarAltitude


@validate_with_pydantic(CalculateSolarAltitudePVLIBInputModel)
def calculate_solar_altitude_pvlib(
        longitude: Longitude,   # degrees
        latitude: Latitude,     # degrees
        timestamp: datetime,
        timezone: ZoneInfo,
    )-> SolarAltitude:
    """Calculate the solar altitude angle in degrees using pvlib"""
    solar_position = pvlib.solarposition.get_solarposition(timestamp, latitude.degrees, longitude.degrees)
    solar_altitude = solar_position['apparent_elevation'].values[0]

    if not isfinite(solar_altitude) or not -90 <= solar_altitude <= 90:
        raise ValueError(f'The calculated solar altitude angle {solar_altitude} is out of the expected range [{-90}, {90}] degrees')

    solar_altitude = SolarAltitude(
        value=solar_altitude,
        unit='degrees',
        position_algorithm='pvlib',
        timing_algorithm='pvlib',
        )

    return solar_altitude
