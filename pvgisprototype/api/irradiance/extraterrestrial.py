from numpy import ndarray
from devtools import debug
from pandas import DatetimeIndex
from pvgisprototype.algorithms.pvis.extraterrestrial import (
    calculate_extraterrestrial_normal_irradiance_series_pvgis,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    PERIGEE_OFFSET,
    SOLAR_CONSTANT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
@custom_cached
def calculate_extraterrestrial_normal_irradiance_series(
    timestamps: DatetimeIndex | None,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
) -> ndarray | dict:
    """
    Calculate the normal extraterrestrial irradiance over a period of time

    Notes
    -----
    Symbol in ... `G0`

    """
    extraterrestrial_normal_irradiance_series = (
        calculate_extraterrestrial_normal_irradiance_series_pvgis(
            timestamps=timestamps,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=extraterrestrial_normal_irradiance_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    extraterrestrial_normal_irradiance_series.build_output(verbose, fingerprint)

    return extraterrestrial_normal_irradiance_series
