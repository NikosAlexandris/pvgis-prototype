from devtools import debug
from zoneinfo import ZoneInfo
import pvlib
from datetime import datetime
from math import isfinite

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarAzimuthPVLIBInputModel
from pvgisprototype import SolarAzimuth
from pvgisprototype import Longitude
from pvgisprototype import Latitude


@validate_with_pydantic(CalculateSolarAzimuthPVLIBInputModel)
def calculate_solar_azimuth_pvlib(
        longitude: Longitude,   # degrees
        latitude: Latitude,     # degrees
        timestamp: datetime,
        timezone: ZoneInfo,
    )-> SolarAzimuth:
    """Calculate the solar azimith (θ) in radians
    """

    solar_position = pvlib.solarposition.get_solarposition(timestamp, latitude.degrees, longitude.degrees)
    solar_azimuth = solar_position['azimuth'].values[0]

    if not isfinite(solar_azimuth) or not 0 <= solar_azimuth <= 360:
        raise ValueError('The `solar_azimuth` should be a finite number ranging in [0, 360] degrees')

    solar_azimuth = SolarAzimuth(
            value=solar_azimuth,
            unit='degrees',
            )

    return solar_azimuth
