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
from pvgisprototype.constants import DEGREES


@validate_with_pydantic(CalculateSolarAzimuthPVLIBInputModel)
def calculate_solar_azimuth_pvlib(
    longitude: Longitude,  # degrees
    latitude: Latitude,  # degrees
    timestamp: datetime,
    timezone: ZoneInfo,
) -> SolarAzimuth:
    """Calculate the solar azimuth (θ) in degrees"""
    solar_position = pvlib.solarposition.get_solarposition(
        timestamp, latitude.degrees, longitude.degrees
    )
    solar_azimuth = solar_position["azimuth"].values[0]

    if (
        not isfinite(solar_azimuth)
        or not solar_azimuth.min_degrees <= solar_azimuth <= solar_azimuth.max_degrees
    ):
        raise ValueError(
            f"The calculated solar azimuth angle {solar_azimuth.degrees} is out of the expected range\
            [{solar_azimuth.min_degrees}, {solar_azimuth.max_degrees}] degrees"
        )
    return SolarAzimuth(
        value=solar_azimuth,
        unit=DEGREES,
        position_algorithm="pvlib",
        timing_algorithm="pvlib",
        origin="North",
    )
