import numpy as np
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import LinkeTurbidityFactor, SolarAltitude, DiffuseIrradiance
from pvgisprototype.algorithms.pvis.diffuse.altitude import (
    calculate_diffuse_solar_altitude_function_series_hofierka,
)
from pvgisprototype.algorithms.pvis.diffuse.transmission_function import (
    calculate_diffuse_transmission_function_series_hofierka,
)
from pvgisprototype.api.irradiance.extraterrestrial import (
    calculate_extraterrestrial_normal_irradiance_series,
)
from pvgisprototype.api.irradiance.limits import (
    LOWER_PHYSICALLY_POSSIBLE_LIMIT,
    UPPER_PHYSICALLY_POSSIBLE_LIMIT,
)
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIFFUSE_HORIZONTAL_IRRADIANCE,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    PERIGEE_OFFSET,
    SOLAR_CONSTANT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
def calculate_diffuse_horizontal_irradiance_series_pvgis(
    timestamps: DatetimeIndex = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    solar_altitude_series: SolarAltitude | None = None,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
):
    """ """
    extraterrestrial_normal_irradiance_series = (
        calculate_extraterrestrial_normal_irradiance_series(
            timestamps=timestamps,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=0,  # no verbosity here by choice!
            log=log,
        )
    )
    # Should this maybe happen already outside this function ? ---------------
    # Suppress negative solar altitude, else we get high-negative diffuse output
    solar_altitude_series.value[solar_altitude_series.value < 0] = np.nan
    # ------------------------------------------------------------------------

    diffuse_horizontal_irradiance_series = (
        extraterrestrial_normal_irradiance_series.value
        * calculate_diffuse_transmission_function_series_hofierka(linke_turbidity_factor_series)
        * calculate_diffuse_solar_altitude_function_series_hofierka(
            solar_altitude_series, linke_turbidity_factor_series
        )
    )
    # ------------------------------------------------------------------------
    diffuse_horizontal_irradiance_series = np.nan_to_num(
        diffuse_horizontal_irradiance_series, nan=0
    )  # safer ? -------------------------------------------------------------

    out_of_range = (
        diffuse_horizontal_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT
    ) | (diffuse_horizontal_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
    if out_of_range.size:
        warning = (
            f"{WARNING_OUT_OF_RANGE_VALUES} in `diffuse_horizontal_irradiance_series`!"
        )
        logger.warning(warning)
        stub_array = np.full(out_of_range.shape, -1, dtype=int)
        index_array = np.arange(len(out_of_range))
        out_of_range_indices = np.where(out_of_range, index_array, stub_array)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=diffuse_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return DiffuseIrradiance(
        value=diffuse_horizontal_irradiance_series,
        unit=IRRADIANCE_UNIT,
        title=DIFFUSE_HORIZONTAL_IRRADIANCE,
        solar_radiation_model=HOFIERKA_2002,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_indices,
        extraterrestrial_normal_irradiance=extraterrestrial_normal_irradiance_series.value,
        linke_turbidity_factor=linke_turbidity_factor_series,
        solar_altitude=solar_altitude_series,
        # position_algorithm=solar_altitude_series.position_algorithm,
        # timing_algorithm=solar_altitude_series.timing_algorithm,
        data_source=HOFIERKA_2002,
    )
