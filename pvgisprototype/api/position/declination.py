from typing import Dict, List
from devtools import debug
from zoneinfo import ZoneInfo

from pandas import DatetimeIndex
from pvgisprototype import SolarDeclination
from pvgisprototype.algorithms.pvis.solar_declination import calculate_solar_declination_series_hofierka
from pvgisprototype.algorithms.pvlib.solar_declination import calculate_solar_declination_series_pvlib
from pvgisprototype.api.position.models import SolarDeclinationModel
from pvgisprototype.api.utilities.conversions import convert_series_to_degrees_if_requested
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_series_noaa
from pvgisprototype.caching import custom_cached
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT, DATA_TYPE_DEFAULT, DEBUG_AFTER_THIS_VERBOSITY_LEVEL, DECLINATION_NAME, HASH_AFTER_THIS_VERBOSITY_LEVEL, LOG_LEVEL_DEFAULT, NOT_AVAILABLE, POSITION_ALGORITHM_NAME, UNIT_NAME, VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RADIANS
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint


@log_function_call
@custom_cached
def model_solar_declination_series(
    timestamps: DatetimeIndex,
    timezone: ZoneInfo = ZoneInfo('UTC'),
    solar_declination_model: SolarDeclinationModel = SolarDeclinationModel.pvis,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = VERBOSE_LEVEL_DEFAULT,
) -> SolarDeclination:
    """ """
    solar_declination_series = None

    if solar_declination_model.value == SolarDeclinationModel.noaa:

        solar_declination_series = calculate_solar_declination_series_noaa(
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )
        solar_declination_series = convert_series_to_degrees_if_requested(
            solar_declination_series,
            angle_output_units,
        )

    if solar_declination_model.value  == SolarDeclinationModel.pvis:
    # if solar_position_model.value == SolarPositionModel.hofierka:

        solar_declination_series = calculate_solar_declination_series_hofierka(
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_declination_model.value  == SolarDeclinationModel.hargreaves:
        pass

    if solar_declination_model.value  == SolarDeclinationModel.pvlib:

        solar_declination_series = calculate_solar_declination_series_pvlib(
            timestamps=timestamps,
            # dtype=dtype,
            # array_backend=array_backend,
            # verbose=verbose,
            # log=log,
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_declination_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return solar_declination_series


def calculate_solar_declination_series(
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_declination_models: List[SolarDeclinationModel] = [SolarDeclinationModel.pvis],
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> Dict:
    """Calculate the solar declination angle

    The solar declination is the angle between the rays of the sun and the
    equator of the earth. It is used to calculate the solar elevation and
    azimuth angles.
    """
    results = {}
    for solar_declination_model in solar_declination_models:
        if solar_declination_model != SolarDeclinationModel.all:  # ignore 'all' in the enumeration
            solar_declination_series = model_solar_declination_series(
                timestamps=timestamps,
                timezone=timezone,
                solar_declination_model=solar_declination_model,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                array_backend=array_backend,
                dtype=dtype,
                verbose=verbose,
                log=log,
            )
            solar_declination_model_series = {  # A less confusing name maybe ?
                solar_declination_model.name: {
                    POSITION_ALGORITHM_NAME: solar_declination_model.value,
                    DECLINATION_NAME: getattr(
                        solar_declination_series, angle_output_units, NOT_AVAILABLE
                    ),
                    UNIT_NAME: angle_output_units,
                }
            }
            results = results | solar_declination_model_series

    return results
