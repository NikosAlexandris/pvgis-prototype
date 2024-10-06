import numpy as np
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import SolarDeclination
from pvgisprototype.algorithms.noaa.fractional_year import (
    calculate_fractional_year_series_noaa,
)
from pvgisprototype.algorithms.noaa.function_models import (
    CalculateSolarDeclinationTimeSeriesNOAAInput,
)
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
@validate_with_pydantic(CalculateSolarDeclinationTimeSeriesNOAAInput)
def calculate_solar_declination_series_noaa(
    timestamps: DatetimeIndex,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output:bool = VALIDATE_OUTPUT_DEFAULT,
) -> SolarDeclination:
    """Calculate the solar declination for a time series.

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
    fractional_year_series = calculate_fractional_year_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
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

    if validate_output:
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
        position_algorithm=fractional_year_series.position_algorithm,
    )
