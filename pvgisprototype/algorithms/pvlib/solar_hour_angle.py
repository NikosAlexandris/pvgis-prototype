from devtools import debug
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import SolarHourAnglePVLIBInput
from pvgisprototype import Longitude
from math import isfinite
from datetime import datetime
from pvgisprototype import SolarHourAngle
import pandas
import pvlib
from pvgisprototype.constants import DEGREES
from pandas import DatetimeIndex
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
import numpy


@validate_with_pydantic(SolarHourAnglePVLIBInput)
def calculate_solar_hour_angle_pvlib(
    longitude: Longitude,
    timestamp: datetime, 
) -> SolarHourAngle:
    """Calculate the solar hour angle in radians.
    """
    equation_of_time = pvlib.solarposition.equation_of_time_spencer71(timestamp.timetuple().tm_yday)
    timestamp = pandas.DatetimeIndex([timestamp.strftime("%Y/%m/%d %H:%M:%S.%f%z")])
    solar_hour_angle = pvlib.solarposition.hour_angle(
        timestamp,
        longitude.degrees,
        equation_of_time=equation_of_time
        )
    solar_hour_angle = SolarHourAngle(
        value=solar_hour_angle[0],
        unit=DEGREES,
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


# @validate_with_pydantic(SolarHourAnglePVLIBInput)
def calculate_solar_hour_angle_series_pvlib(
    longitude: Longitude,
    timestamps: DatetimeIndex,
) -> SolarHourAngle:
    """Calculate the solar hour angle in radians.
    """
    equation_of_time_series = pvlib.solarposition.equation_of_time_spencer71(timestamps.dayofyear)
    solar_hour_angle_series = pvlib.solarposition.hour_angle(
        timestamps,
        longitude.degrees,
        equation_of_time=equation_of_time_series
        )
    if not numpy.all(
        (SolarHourAngle().min_degrees <= solar_hour_angle_series)
        & (solar_hour_angle_series <= SolarHourAngle().max_degrees)
    ):
        out_of_range_values = solar_hour_angle_series[
            ~(
                (-SolarHourAngle().min_degrees <= solar_hour_angle_series)
                & (solar_hour_angle_series <= SolarHourAngle().max_degrees)
            )
        ]
        raise ValueError(
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{SolarHourAngle().min_degrees}, {SolarHourAngle().max_degrees}] degrees"
            f" in [code]solar_hour_angle_series[/code] : {numpy.degrees(out_of_range_values)}"
        )
    return SolarHourAngle(
        value=solar_hour_angle_series,
        unit=DEGREES,
        position_algorithm='pvlib (Spencer 1971)',
        timing_algorithm='pvlib',
    )
