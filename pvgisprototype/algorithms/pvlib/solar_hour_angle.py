from devtools import debug
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import SolarHourAnglePVLIBInput
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype import Longitude
from datetime import datetime
from pvgisprototype import SolarHourAngle
from math import pi
import pvlib
import pandas as pd


@validate_with_pydantic(SolarHourAnglePVLIBInput)
def calculate_solar_hour_angle_pvlib(
    longitude: Longitude,
    timestamp: datetime, 
    angle_output_units: str = 'radians',
) -> SolarHourAngle:
    """Calculate the solar hour angle in radians.
    """
    equation_of_time = pvlib.solarposition.equation_of_time_spencer71(timestamp.timetuple().tm_yday)
    
    longitude = convert_to_degrees_if_requested(longitude, 'degrees')

    timestamp = pd.DatetimeIndex([timestamp.strftime("%Y/%m/%d %H:%M:%S.%f%z")])

    solar_hour_angle = pvlib.solarposition.hour_angle(
        timestamp,
        longitude.value,
        equation_of_time=equation_of_time
        )

    if angle_output_units == 'degrees' and not -180 <= solar_hour_angle <= 180:
        raise ValueError(f'The calculated hour angle {solar_hour_angle} is out of the expected range [{-180}, {180}] degrees')

    solar_hour_angle = SolarHourAngle(
        value=solar_hour_angle,
        unit='degrees',
    )
    solar_hour_angle = convert_to_degrees_if_requested(solar_hour_angle, angle_output_units)

    return solar_hour_angle