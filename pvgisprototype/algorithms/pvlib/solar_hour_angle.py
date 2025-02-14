import numpy
import pvlib
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Longitude, SolarHourAngle
from pvgisprototype.api.position.models import SolarPositionModel, SolarTimeModel
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DEGREES,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint
from pvgisprototype.validation.functions import (
    SolarHourAngleSeriesPVLIBInput,
    validate_with_pydantic,
)


@custom_cached
@validate_with_pydantic(SolarHourAngleSeriesPVLIBInput)
def calculate_solar_hour_angle_series_pvlib(
    longitude: Longitude,
    timestamps: DatetimeIndex,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarHourAngle:
    """Calculate the solar hour angle in radians."""
    equation_of_time_series = pvlib.solarposition.equation_of_time_spencer71(
        timestamps.dayofyear
    )
    solar_hour_angle_series = pvlib.solarposition.hour_angle(
        timestamps, longitude.degrees, equation_of_time=equation_of_time_series
    ).to_numpy()
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

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_hour_angle_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarHourAngle(
        value=solar_hour_angle_series,
        unit=DEGREES,
        position_algorithm=SolarPositionModel.pvlib,
        timing_algorithm=SolarTimeModel.pvlib + " (Spencer 1971)",
    )
