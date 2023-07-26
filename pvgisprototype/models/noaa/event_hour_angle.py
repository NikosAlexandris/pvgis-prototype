from devtools import debug

from .noaa_models import CalculateEventHourAngleNOAAInput
from .decorators import validate_with_pydantic
from .noaa_models import Latitude
from datetime import datetime
from .solar_declination import calculate_solar_declination_noaa
from math import cos
from math import tan
from math import acos
from typing import NamedTuple
from pvgisprototype.api.named_tuples import generate


@validate_with_pydantic(CalculateEventHourAngleNOAAInput)
def calculate_event_hour_angle_noaa(
        latitude: Latitude,
        timestamp: datetime,
        refracted_solar_zenith: float = 1.5853349194640094,  # radians
        angle_units: str = 'radians',
        angle_output_units: str = 'radians',
        ):
    """
    """
    debug(locals())
    solar_declination = calculate_solar_declination_noaa(
            timestamp,
            angle_units,
            angle_output_units,
            )  # radians
    cosine_event_hour_angle = cos(refracted_solar_zenith) / (
        cos(latitude) * cos(solar_declination.value)
    ) - tan(latitude) * tan(solar_declination.value)
    event_hour_angle = acos(cosine_event_hour_angle)  # radians

    event_hour = generate(
        'event_time'.upper(),
        (event_hour_angle, angle_output_units),
    )

    # # ------------------------------------------------------------------------
    # if angle_output_units == 'degrees':  # is this ever needed?
    #     event_hour_angle = convert_to_degrees_if_requested(
    #             event_hour_angle,
    #             angle_output_units,
    #             )
    # # ------------------------------------------------------------------------

    debug(locals())
    return event_hour
