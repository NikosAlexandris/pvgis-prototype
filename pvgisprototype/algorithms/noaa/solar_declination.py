from devtools import debug
from datetime import datetime
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarDeclinationNOAAInput
from pvgisprototype.validation.functions import CalculateSolarDeclinationNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarDeclinationTimeSeriesNOAAInput
from .fractional_year import calculate_fractional_year_noaa 
from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_time_series_noaa
from math import sin
from math import cos
from math import isfinite
import numpy as np
from pvgisprototype import SolarDeclination
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pandas import DatetimeIndex
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES


@validate_with_pydantic(CalculateSolarDeclinationNOAAInput)
def calculate_solar_declination_noaa(
    timestamp: datetime,
) -> SolarDeclination:
    """Calculate the solar declination angle in radians"""
    fractional_year = calculate_fractional_year_noaa(
        timestamp=timestamp,
    )
    declination = (
        0.006918
        - 0.399912 * cos(fractional_year.radians)
        + 0.070257 * sin(fractional_year.radians)
        - 0.006758 * cos(2 * fractional_year.radians)
        + 0.000907 * sin(2 * fractional_year.radians)
        - 0.002697 * cos(3 * fractional_year.radians)
        + 0.00148 * sin(3 * fractional_year.radians)
        )
    solar_declination = SolarDeclination(
        value=declination,
        unit=RADIANS,
        position_algorithm='NOAA',
        timing_algorithm='NOAA'
    )
    if (
        not isfinite(solar_declination.degrees)
        or not solar_declination.min_degrees <= solar_declination.degrees <= solar_declination.max_degrees
    ):
        raise ValueError(
            f"The calculated solar declination angle {solar_declination.degrees} is out of the expected range\
            [{solar_declination.min_degrees}, {solar_declination.max_degrees}] degrees"
        )
    return solar_declination


@log_function_call
@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateSolarDeclinationTimeSeriesNOAAInput)
def calculate_solar_declination_time_series_noaa(
    timestamps: DatetimeIndex,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> SolarDeclination:
    """

    Notes
    -----
    From NOAA's .. Excel sheet:

    sine_solar_declination
    = ASIN(
        SIN(RADIANS(R2))*SIN(RADIANS(P2))
    )

    where:

    P2 = M2-0.00569-0.00478*SIN(RADIANS(125.04-1934.136*G2))

        where:

        M2 = Geom Mean Long Sun (deg) + Geom Mean Anom Sun (deg)


    R2 = Q2 + 0.00256 * COS(RADIANS(125.04 - 1934.136*G2))

        where :

       Q2 = Mean Obliq Ecliptic (deg)


    """
    fractional_year_series = calculate_fractional_year_time_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    solar_declination_series = (
        0.006918
        - 0.399912 * np.cos(fractional_year_series.radians)
        + 0.070257 * np.sin(fractional_year_series.radians)
        - 0.006758 * np.cos(2 * fractional_year_series.radians)
        + 0.000907 * np.sin(2 * fractional_year_series.radians)
        - 0.002697 * np.cos(3 * fractional_year_series.radians)
        + 0.00148 * np.sin(3 * fractional_year_series.radians)
    )
    if not np.all(
        (SolarDeclination().min_radians <= solar_declination_series)
        & (solar_declination_series <= SolarDeclination().max_radians)
    ):
        index_of_out_of_range_values = np.where(
            (solar_declination_series < SolarDeclination().min_radians)
            | (solar_declination_series > SolarDeclination().max_radians)
        )
        out_of_range_values = solar_declination_series[index_of_out_of_range_values]
        raise ValueError(
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{SolarDeclination().min_degrees}, {SolarDeclination().max_degrees}] degrees"
            f" in [code]solar_declination_series[/code] : {np.degrees(out_of_range_values)}"
        )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=solar_declination_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return SolarDeclination(
        value=solar_declination_series,
        unit=RADIANS,
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
    )
