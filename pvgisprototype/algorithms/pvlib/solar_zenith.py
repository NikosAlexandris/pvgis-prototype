from devtools import debug
from zoneinfo import ZoneInfo
import pvlib
from datetime import datetime
from math import isfinite

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarZenithPVLIBInputModel
from pvgisprototype import SolarZenith
from pvgisprototype import Longitude
from pvgisprototype import Latitude


@validate_with_pydantic(CalculateSolarZenithPVLIBInputModel)
def calculate_solar_zenith_pvlib(
        longitude: Longitude,   # degrees
        latitude: Latitude,     # degrees
        timestamp: datetime,
        timezone: ZoneInfo,
    )-> SolarZenith:
    """Calculate the solar azimith (θ) in radians
    """

    solar_position = pvlib.solarposition.get_solarposition(timestamp, latitude.degrees, longitude.degrees)
    solar_position = pvlib.solarposition.get_solarposition(timestamp, latitude.degrees, longitude.degrees)
    solar_zenith = solar_position['zenith'].values[0]

    solar_zenith = SolarZenith(
            value=solar_zenith,
            unit='degrees',
            position_algorithm='pvlib',
            timing_algorithm='pvlib',
            )
    # if not isfinite(solar_zenith) or not 0 <= solar_zenith <= 180.836518:
    #     raise ValueError('The `solar_zenith` should be a finite number ranging in [0, 180.836518] degrees')
    if (
        not isfinite(solar_zenith.degrees)
        or not solar_zenith.min_degrees <= solar_zenith.degrees <= solar_zenith.max_degrees
    ):
        raise ValueError(
            f"The calculated solar zenith angle {solar_zenith.degrees} is out of the expected range\
            [{solar_zenith.min_degrees}, {solar_zenith.max_degrees}] degrees"
        )
    return solar_zenith
