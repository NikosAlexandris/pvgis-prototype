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
from pvgisprototype.constants import DEGREES


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

    solar_altitude = SolarAltitude(
        value=solar_altitude,
        unit=DEGREES,
        position_algorithm='PVLIB',
        timing_algorithm='PVLIB',
    )
    if (
        not isfinite(solar_altitude.degrees)
        or not solar_altitude.min_degrees <= solar_altitude.degrees <= solar_altitude.max_degrees
    ):
        raise ValueError(
            f"The calculated solar altitude angle {solar_altitude.degrees} is out of the expected range\
            [{solar_altitude.min_degrees}, {solar_altitude.max_degrees}] degrees"
        )
    return solar_altitude
