"""
This Python module is part of PVGIS' API. It implements functions to calculate
the direct solar irradiance.

_Direct_ or _beam_ irradiance is one of the main components of solar
irradiance. It comes perpendicular from the Sun and is not scattered before it
irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _direct_ irradiance.
"""

import numpy as np
from devtools import debug
from pandas import DatetimeIndex

from xarray import DataArray
from pvgisprototype import (
    NormalIrradiance,
    Irradiance,
    LinkeTurbidityFactor,
    OpticalAirMass,
    SolarAltitude,
)
from pvgisprototype.algorithms.pvis.direct.linke_turbidity_factor import (
    correct_linke_turbidity_factor_series,
)
from pvgisprototype.api.irradiance.direct.rayleigh_optical_thickness import (
    calculate_rayleigh_optical_thickness_series,
)
from pvgisprototype.algorithms.pvis.extraterrestrial import (
    calculate_extraterrestrial_normal_irradiance_series_pvgis,
)
from pvgisprototype.api.irradiance.limits import (
    LOWER_PHYSICALLY_POSSIBLE_LIMIT,
    UPPER_PHYSICALLY_POSSIBLE_LIMIT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIRECT_NORMAL_IRRADIANCE,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT,
    PERIGEE_OFFSET,
    SOLAR_CONSTANT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
@custom_cached
def calculate_direct_normal_irradiance_series_pvgis(
    timestamps: DatetimeIndex | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    optical_air_mass_series: OpticalAirMass = [
        OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT
    ],  # REVIEW-ME + ?
    clip_to_physically_possible_limits: bool = True,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> Irradiance:
    """Calculate the direct normal irradiance.

    The direct normal irradiance represents the amount of solar radiation
    received per unit area by a surface that is perpendicular (normal) to the
    rays that come in a straight line from the direction of the sun at its
    current position in the sky.

    This function implements the algorithm described by Hofierka, 2002. [1]_

    Notes
    -----
    Known also as : SID, units : W*m-2

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    extraterrestrial_normal_irradiance_series = (
        calculate_extraterrestrial_normal_irradiance_series_pvgis(
            timestamps=timestamps,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
        )
    )
    corrected_linke_turbidity_factor_series = correct_linke_turbidity_factor_series(
        linke_turbidity_factor_series,
        verbose=verbose,
    )
    rayleigh_optical_thickness_series = calculate_rayleigh_optical_thickness_series(
        optical_air_mass_series,
        verbose=verbose,
    )  # _quite_ high when the sun is below the horizon. Makes sense ?

    # Calculate
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        exponent = (
            corrected_linke_turbidity_factor_series.value
            * optical_air_mass_series.value
            * rayleigh_optical_thickness_series.value
        )
        direct_normal_irradiance_series = extraterrestrial_normal_irradiance_series.value * np.exp(exponent)

    # Warning
    out_of_range = (
        direct_normal_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT
    ) | (direct_normal_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
    if out_of_range.size > 0:
        out_of_range_values = direct_normal_irradiance_series[out_of_range]
        stub_array = np.full(out_of_range.shape, -1, dtype=int)
        index_array = np.arange(len(out_of_range))
        out_of_range_indices = np.where(out_of_range, index_array, stub_array)
        warning_unstyled = (
            f"\n"
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
            f" in direct_normal_irradiance_series : "
            f"{out_of_range_values}"
            f"\n"
        )
        warning = (
            f"\n"
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
            f" in [code]direct_normal_irradiance_series[/code] : "
            f"{out_of_range_values}"
            f"\n"
        )
        logger.warning(warning_unstyled, alt=warning)

        # Clip irradiance values to the lower and upper
        # physically possible limits
        if clip_to_physically_possible_limits:
            direct_normal_irradiance_series = np.clip(
                direct_normal_irradiance_series, LOWER_PHYSICALLY_POSSIBLE_LIMIT,
                UPPER_PHYSICALLY_POSSIBLE_LIMIT
            )
        warning_2_unstyled = (
            f"\n"
            f"Out-of-Range values in direct_normal_irradiance_series"
            f"clipped to physically possible limits "
            f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
            f"\n"
        )
        warning_2 = (
            f"\n"
            f"Out-of-Range values in [code]direct_normal_irradiance_series[/code]"
            f"clipped to physically possible limits "
            f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
            f"\n"
        )
        logger.warning(warning_2_unstyled, alt=warning_2)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_normal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return NormalIrradiance(
        value=direct_normal_irradiance_series,
        unit=IRRADIANCE_UNIT,
        title=DIRECT_NORMAL_IRRADIANCE,
        solar_radiation_model=HOFIERKA_2002,
        extraterrestrial_normal_irradiance=extraterrestrial_normal_irradiance_series.value,
        linke_turbidity_factor=linke_turbidity_factor_series,
        linke_turbidity_factor_adjusted=corrected_linke_turbidity_factor_series,
        rayleigh_optical_thickness=rayleigh_optical_thickness_series,
        optical_air_mass=optical_air_mass_series,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_indices,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
    )


@log_function_call
@custom_cached
def calculate_direct_normal_from_horizontal_irradiance_series_pvgis(
    direct_horizontal_irradiance: DataArray,
    solar_altitude_series: SolarAltitude | None = None,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
) -> Irradiance:
    """Calculate the direct normal from the horizontal irradiance.

    The direct normal irradiance represents the amount of solar radiation
    received per unit area by a surface that is perpendicular (normal) to the
    rays that come in a straight line from the direction of the sun at its
    current position in the sky.

    This function calculates the normal irradiance from the given horizontal
    irradiance component.

    Notes
    -----
    Known also as : SID, units : W*m-2

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    mask_solar_altitude_positive = solar_altitude_series.radians > 0
    mask_not_in_shade = np.full_like(
        solar_altitude_series.radians, True
    )  # Stub, replace with actual condition
    mask = np.logical_and.reduce((mask_solar_altitude_positive, mask_not_in_shade))

    direct_normal_irradiance_series = np.zeros_like(solar_altitude_series.radians)
    if np.any(mask):
        direct_normal_irradiance_series[mask] = (
            direct_horizontal_irradiance / np.sin(solar_altitude_series.radians)
        )[mask]

    # Warning
    out_of_range = (
        direct_normal_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT
    ) | (direct_normal_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
    if out_of_range.size > 0:
        out_of_range_values = direct_normal_irradiance_series[out_of_range]
        stub_array = np.full(out_of_range.shape, -1, dtype=int)
        index_array = np.arange(len(out_of_range))
        out_of_range_indices = np.where(out_of_range, index_array, stub_array)
        warning_unstyled = (
            f"\n"
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
            f" in direct_normal_irradiance_series : "
            f"{out_of_range_values}"
            f"\n"
        )
        warning = (
            f"\n"
            f"{WARNING_OUT_OF_RANGE_VALUES} "
            f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
            f" in [code]direct_normal_irradiance_series[/code] : "
            f"{out_of_range_values}"
            f"\n"
        )
        logger.warning(warning_unstyled, alt=warning)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_normal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return NormalIrradiance(
        value=direct_normal_irradiance_series,
        unit=IRRADIANCE_UNIT,
        title=DIRECT_NORMAL_IRRADIANCE,
        solar_radiation_model=HOFIERKA_2002,
        direct_horizontal_irradiance=direct_horizontal_irradiance,
        solar_altitude=solar_altitude_series,
        # solar_position_algorithm=solar_position_model,
        # solar_time_algorithm=solar_time_model,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_indices,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
    )
