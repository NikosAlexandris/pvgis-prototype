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
    """Calculate the solar zenith angle (φ) in radians
    """

    solar_position = pvlib.solarposition.get_solarposition(timestamp, latitude.degrees, longitude.degrees)
    solar_altitude = solar_position['apparent_elevation'].values[0]

    if not isfinite(solar_altitude) or not -90 <= solar_altitude <= 90:
        raise ValueError(f'The `solar_altitude` should be a finite number ranging in [{-90}, {90}] degrees')

    return SolarAltitude(value=solar_altitude, unit='degrees')
