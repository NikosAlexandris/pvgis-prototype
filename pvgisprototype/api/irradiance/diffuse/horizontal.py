from zoneinfo import ZoneInfo

import numpy as np
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Irradiance, LinkeTurbidityFactor
from pvgisprototype.api.irradiance.diffuse.altitude import (
    calculate_diffuse_solar_altitude_function_series,
    diffuse_transmission_function_series,
)
from pvgisprototype.api.irradiance.extraterrestrial import (
    calculate_extraterrestrial_normal_irradiance_series,
)
from pvgisprototype.api.irradiance.limits import (
    LOWER_PHYSICALLY_POSSIBLE_LIMIT,
    UPPER_PHYSICALLY_POSSIBLE_LIMIT,
)
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ALTITUDE_COLUMN_NAME,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIFFUSE_HORIZONTAL_IRRADIANCE,
    DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_COLUMN_NAME,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    PERIGEE_OFFSET,
    RADIANS,
    RADIATION_MODEL_COLUMN_NAME,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    TITLE_KEY_NAME,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.core.hashing import generate_hash


@log_function_call
def calculate_diffuse_horizontal_irradiance_series(
    longitude: float,
    latitude: float,
    timestamps: DatetimeIndex = None,
    timezone: ZoneInfo | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
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
    # extraterrestrial on a horizontal surface requires the solar altitude
    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        # refracted_solar_zenith=refracted_solar_zenith,
        # solar_time_model=solar_time_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,  # Is this wanted here ? i.e. not setting = 0 ?
        log=log,
    )
    # Suppress negative solar altitude, else we get high-negative diffuse output
    solar_altitude_series.value[solar_altitude_series.value < 0] = np.nan

    diffuse_horizontal_irradiance_series = (
        extraterrestrial_normal_irradiance_series.value
        * diffuse_transmission_function_series(linke_turbidity_factor_series)
        * calculate_diffuse_solar_altitude_function_series(
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

    components_container = {
        "main": lambda: {
            TITLE_KEY_NAME: DIFFUSE_HORIZONTAL_IRRADIANCE,
            DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series,
        },  # if verbose > 0 else {},
        "extended": lambda: (
            {
                RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
            }
            if verbose > 1
            else {}
        ),
        "more_extended": lambda: (
            {
                TITLE_KEY_NAME: DIFFUSE_HORIZONTAL_IRRADIANCE
                + " & relevant components",
                EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: extraterrestrial_normal_irradiance_series.value,
                ALTITUDE_COLUMN_NAME: (
                    getattr(solar_altitude_series, angle_output_units)
                    if solar_altitude_series
                    else None
                ),
                LINKE_TURBIDITY_COLUMN_NAME: linke_turbidity_factor_series.value,
            }
            if verbose > 2
            else {}
        ),
        "even_more_extended": lambda: {} if verbose > 3 else {},
        "and_even_more_extended": lambda: {} if verbose > 4 else {},
        "extra": lambda: {} if verbose > 5 else {},
        "out-of-range": lambda: (
            {
                # OUT_OF_RANGE_INDICES_COLUMN_NAME: out_of_range,
                # OUT_OF_RANGE_INDICES_COLUMN_NAME + ' i': out_of_range_indices,
            }
            if out_of_range_indices[0].size > 0
            else {}
        ),
        "fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    diffuse_horizontal_irradiance_series
                ),
            }
            if fingerprint
            else {}
        ),
    }

    components = {}
    for key, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=diffuse_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
        value=diffuse_horizontal_irradiance_series,
        unit=IRRADIANCE_UNIT,
        position_algorithm="",
        timing_algorithm="",
        elevation=None,
        surface_orientation=None,
        surface_tilt=None,
        components=components,
    )
