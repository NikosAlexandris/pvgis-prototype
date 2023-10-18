from devtools import debug
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import SolarHourAnglePVLIBInput
from pvgisprototype import Longitude
from datetime import datetime
from pvgisprototype import SolarHourAngle
import pvlib
import pandas as pd
import pandas as pd
from pvgisprototype.constants import DEGREES


@validate_with_pydantic(SolarHourAnglePVLIBInput)
def calculate_solar_hour_angle_pvlib(
    longitude: Longitude,
    timestamp: datetime, 
) -> SolarHourAngle:
    """Calculate the solar hour angle in radians.
    """
    equation_of_time = pvlib.solarposition.equation_of_time_spencer71(timestamp.timetuple().tm_yday)
    
    timestamp = pd.DatetimeIndex([timestamp.strftime("%Y/%m/%d %H:%M:%S.%f%z")])
    equation_of_time = pvlib.solarposition.equation_of_time_spencer71(timestamp.timetuple().tm_yday)
    
    timestamp = pd.DatetimeIndex([timestamp.strftime("%Y/%m/%d %H:%M:%S.%f%z")])

    solar_hour_angle = pvlib.solarposition.hour_angle(
        timestamp,
        longitude.degrees,
        equation_of_time=equation_of_time
        )
    solar_hour_angle = pvlib.solarposition.hour_angle(
        timestamp,
        longitude.degrees,
        equation_of_time=equation_of_time
        )

    solar_hour_angle = SolarHourAngle(
        value=solar_hour_angle,
        unit=DEGREES,
        position_algorithm='PVLIB',
        timing_algorithm='PVLIB',
    )

    if not -180 <= solar_hour_angle.degrees <= 180:
        raise ValueError(f'The calculated hour angle {solar_hour_angle} is out of the expected range [{-180}, {180}] degrees')
    return solar_hour_angle
