from devtools import debug
from typing import Union
from typing import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype import SolarDeclination
from pvgisprototype.api.geometry.models import SolarDeclinationModels
from pvgisprototype.api.utilities.conversions import convert_series_to_degrees_if_requested
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RADIANS
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from cachetools import cached
from pvgisprototype.caching import custom_hashkey


@log_function_call
@cached(cache={}, key=custom_hashkey)
def model_solar_declination_time_series(
    timestamps: Union[datetime, Sequence[datetime]],
    timezone: ZoneInfo = None,
    model: SolarDeclinationModels = SolarDeclinationModels.pvis,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    verbose: int = 0,
    log: int = 0,
) -> Sequence[SolarDeclination]:
    """ """
    if model.value == SolarDeclinationModels.noaa:

        solar_declination_series = calculate_solar_declination_time_series_noaa(
            timestamps=timestamps,
            angle_output_units=angle_output_units
        )
        solar_declination_series = convert_series_to_degrees_if_requested(
            solar_declination_series,
            angle_output_units,
        )

    if model.value  == SolarDeclinationModels.pvis:
        pass

    if model.value  == SolarDeclinationModels.hargreaves:
        pass

    if model.value  == SolarDeclinationModels.pvlib:
        pass

    log_data_fingerprint(
        data=solar_declination_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return solar_declination_series
