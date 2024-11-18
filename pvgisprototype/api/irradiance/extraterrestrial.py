from numpy import ndarray
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import ExtraterrestrialIrradiance
from pvgisprototype.algorithms.pvis.extraterrestrial import calculate_extraterrestrial_normal_irradiance_series_pvgis
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DAY_ANGLE_SERIES,
    DAY_OF_YEAR_COLUMN_NAME,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DISTANCE_CORRECTION_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    EXTRATERRESTRIAL_NORMAL_IRRADIANCE,
    EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    IRRADIANCE_UNIT,
    PERIGEE_OFFSET,
    SOLAR_CONSTANT,
    TITLE_KEY_NAME,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.hashing import generate_hash


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

    components_container = {
        "Extraterrestrial Irradiance": lambda: {
            TITLE_KEY_NAME: EXTRATERRESTRIAL_NORMAL_IRRADIANCE,
            EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: extraterrestrial_normal_irradiance_series.value,
        },
        "Metadata": lambda: (
            {
                DAY_OF_YEAR_COLUMN_NAME: extraterrestrial_normal_irradiance_series.day_of_year,
                DAY_ANGLE_SERIES: extraterrestrial_normal_irradiance_series.day_angle,
                DISTANCE_CORRECTION_COLUMN_NAME: extraterrestrial_normal_irradiance_series.distance_correction_factor,
            }
            if verbose > 1
            else {}
        ),
        "Fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    extraterrestrial_normal_irradiance_series.value
                ),
            }
            if fingerprint
            else {}
        ),
    }

    components = {}
    for _, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=extraterrestrial_normal_irradiance_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return ExtraterrestrialIrradiance(
        value=extraterrestrial_normal_irradiance_series.value,
        unit=IRRADIANCE_UNIT,
        day_angle=extraterrestrial_normal_irradiance_series.day_angle,
        solar_constant=extraterrestrial_normal_irradiance_series.solar_constant,
        perigee_offset=extraterrestrial_normal_irradiance_series.perigee_offset,
        eccentricity_correction_factor=extraterrestrial_normal_irradiance_series.eccentricity_correction_factor,
        components=components,
    )
