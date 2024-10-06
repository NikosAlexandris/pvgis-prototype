from zoneinfo import ZoneInfo

import numpy as np
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Longitude, SolarHourAngle
from pvgisprototype.algorithms.noaa.function_models import (
    CalculateSolarHourAngleTimeSeriesNOAAInput,
)
from pvgisprototype.algorithms.noaa.solar_time import (
    calculate_true_solar_time_series_noaa,
)
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.functions import validate_with_pydantic


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateSolarHourAngleTimeSeriesNOAAInput)
def calculate_solar_hour_angle_series_noaa(
    longitude: Longitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output:bool = VALIDATE_OUTPUT_DEFAULT
) -> SolarHourAngle:
    """Calculate the solar hour angle for a time series.

    The solar hour angle calculation converts the local solar time (LST) into
    the number of degrees which the sun moves across the sky. In other words,
    it reflects the Earth's rotation and indicates the time of the day relative
    to the position of the Sun. It bases on the longitude and timestamp and by
    definition, the solar hour angle is :

      - 0° at solar noon
      - negative in the morning
      - positive in the afternoon.

    Since the Earth rotates 15° per hour (or pi / 12 in radians), each hour
    away from solar noon corresponds to an angular motion of the sun in the sky
    of 15°. Practically, the calculation converts a timestamp into a solar
    time.

    Parameters
    ----------

    Returns
    -------

    Notes
    -----
    In the "original" equation, the solar hour angle is measured in degrees.

        `hour_angle = true_solar_time / 4 - 180`

        which is the same as

        `hour_angle = true_solar_time * 0.25 - 180`

    In the present implementation, we calculate the solar hour angle directly
    in radians. A full circle corresponds to 360 degrees or 2π radians. With
    1440 minutes in a day, the angular change per minute is calculated as 2π
    radians divided by 1440 minutes. This results in approximately
    0.004363323129985824 radians per minute.

    To find the solar hour angle, we first calculate the time difference from
    solar noon (by subtracting the true solar time in minutes from 720). We
    then multiply this difference by the angular change per minute
    (0.004363323129985824) to convert the time difference into radians. This
    approach (accurately?) represents the solar hour angle as an angular
    measurement in radians, reflecting the Earth's rotation and the position of
    the sun in the sky relative to a given location on Earth.

    In NREL's SPA ... , equation 32:

        Η = ν + σ − α

        Where :
            - σ the observer geographical longitude, positive or negative
              for east or west of Greenwich, respectively.

        Limit Η to the range from 0 to 360 degrees using step 3.2.6 and note that it
        is measured westward from south in this algorithm.

        Step 3.2.6 :

            Limit L to the range from 0 to 360 degrees. That can be
            accomplished by dividing L by 360 and recording the decimal
            fraction of the division as F. If L is positive, then the limited L
            = 360 * F. If L is negative, then the limited L = 360 - 360 * F.

    """
    true_solar_time_series = calculate_true_solar_time_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
    )
    solar_hour_angle_series = (true_solar_time_series.minutes - 720.0) * (np.pi / 720.0)
    # solar_hour_angle_series = np.where(
    #         # true_solar_time_series.minutes < 0,
    #         solar_hour_angle_series < 0,
    #         solar_hour_angle_series + pi,
    #         solar_hour_angle_series - pi,
    #         )

    if validate_output:
        if not np.all(
            (SolarHourAngle().min_radians <= solar_hour_angle_series)
            & (solar_hour_angle_series <= SolarHourAngle().max_radians)
        ):
            out_of_range_values = solar_hour_angle_series[
                ~(
                    (-SolarHourAngle().min_radians <= solar_hour_angle_series)
                    & (solar_hour_angle_series <= SolarHourAngle().max_radians)
                )
            ]
            raise ValueError(
                f"{WARNING_OUT_OF_RANGE_VALUES} "
                f"[{SolarHourAngle().min_degrees}, {SolarHourAngle().max_degrees}] degrees"
                f" in [code]solar_hour_angle_series[/code] : {np.degrees(out_of_range_values)}"
            )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_hour_angle_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarHourAngle(
        value=solar_hour_angle_series,
        unit=RADIANS,
        position_algorithm=SolarPositionModel.noaa,
        timing_algorithm=true_solar_time_series.timing_algorithm,
    )
