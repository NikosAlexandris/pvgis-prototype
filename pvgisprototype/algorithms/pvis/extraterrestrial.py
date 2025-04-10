from numpy import ndarray, unique, pi, cos
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import ExtraterrestrialIrradiance
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    IRRADIANCE_UNIT,
    PERIGEE_OFFSET,
    SOLAR_CONSTANT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call


def get_days_per_year(years):
    return 365 + ((years % 4 == 0) & ((years % 100 != 0) | (years % 400 == 0))).astype(
        int
    )


@log_function_call
@custom_cached
def calculate_extraterrestrial_normal_irradiance_series_pvgis(
    timestamps: DatetimeIndex | None,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
) -> ndarray | dict:
    """
    Calculate the normal extraterrestrial irradiance over a period of time

    Notes
    -----
    Symbol in ... `G0`

    """
    years_in_timestamps = timestamps.year
    years, indices = unique(years_in_timestamps, return_inverse=True)
    days_per_year = get_days_per_year(years).astype(dtype)
    days_in_years = days_per_year[indices]
    day_of_year_series = timestamps.dayofyear.to_numpy().astype(dtype)
    # day angle == fractional year, hence : use model_fractional_year_series()
    day_angle_series = 2 * pi * day_of_year_series / days_in_years
    distance_correction_factor_series = 1 + eccentricity_correction_factor * cos(
        day_angle_series - perigee_offset
    )
    extraterrestrial_normal_irradiance_series = (
        solar_constant * distance_correction_factor_series
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=extraterrestrial_normal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return ExtraterrestrialIrradiance(
        name="Extraterrestrial Solar Irradiance",
        shortname="Extra",
        title="Extraterrestrial Normal Irradiance",
        # name_and_symbol=EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME,
        value=extraterrestrial_normal_irradiance_series,
        unit=IRRADIANCE_UNIT,
        timestamps=timestamps,
        day_of_year=day_of_year_series,
        day_angle=day_angle_series,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        distance_correction_factor=distance_correction_factor_series,
        data_source="PVGIS 6",
        quality="Not validated!",
    )
