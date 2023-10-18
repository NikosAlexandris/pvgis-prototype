from devtools import debug
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import SolarHourAnglePVLIBInput
from pvgisprototype import Longitude
from math import isfinite
from datetime import datetime
from pvgisprototype import SolarHourAngle
import pvlib
import pandas as pd


@validate_with_pydantic(SolarHourAnglePVLIBInput)
def calculate_solar_hour_angle_pvlib(
    longitude: Longitude,
    timestamp: datetime, 
) -> SolarHourAngle:
    """Calculate the solar hour angle in radians.
    """
    equation_of_time = pvlib.solarposition.equation_of_time_spencer71(timestamp.timetuple().tm_yday)
    
    timestamp = pd.DatetimeIndex([timestamp.strftime("%Y/%m/%d %H:%M:%S.%f%z")])

    solar_hour_angle = pvlib.solarposition.hour_angle(
        timestamp,
        longitude.degrees,
        equation_of_time=equation_of_time
        )

    solar_hour_angle = SolarHourAngle(
        value=solar_hour_angle,
        unit='degrees',
        position_algorithm='pvlib',
        timing_algorithm='pvlib',
    )
    if (
        not isfinite(solar_hour_angle.degrees)
        or not solar_hour_angle.min_degrees <= solar_hour_angle.degrees <= solar_hour_angle.max_degrees
    ):
        raise ValueError(
            f"The calculated solar hour angle {solar_hour_angle.degrees} is out of the expected range\
            [{solar_hour_angle.min_degrees}, {solar_hour_angle.max_degrees}] degrees"
        )
    return solar_hour_angle
