"""
This Python module is part of PVGIS' Algorithms. It implements a function to
calculate the direct normal solar irradiance.

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

from pvgisprototype import (
    DirectNormalIrradiance,
    LinkeTurbidityFactor,
    OpticalAirMass,
)
from pvgisprototype.algorithms.hofierka.irradiance.direct.clear_sky.linke_turbidity_factor import (
    correct_linke_turbidity_factor_series,
)
from pvgisprototype.api.irradiance.direct.rayleigh_optical_thickness import (
    calculate_rayleigh_optical_thickness_series,
)
from pvgisprototype.algorithms.hofierka.irradiance.extraterrestrial.normal import (
    calculate_extraterrestrial_normal_irradiance_hofierka,
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
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT,
    PERIGEE_OFFSET,
    SOLAR_CONSTANT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
@custom_cached
def calculate_direct_normal_irradiance_hofierka(
    timestamps: DatetimeIndex | None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    optical_air_mass_series: OpticalAirMass = [
        OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT
    ],  # REVIEW-ME + ?
    clip_to_physically_possible_limits: bool = True,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> DirectNormalIrradiance:
    """Calculate the direct normal irradiance.

    The direct normal irradiance attenuated by the cloudless atmosphere,
    represents the amount of solar radiation received per unit area by a
    surface that is perpendicular (normal) to the rays that come in a straight
    line from the direction of the sun at its current position in the sky.

    This function implements the algorithm described by Hofierka, 2002. [1]_


    Notes
    -----
    B0c = G0 exp {-0.8662 TLK m δR(m)}

    where :
    - -0.8662 TLK is the air mass 2 Linke atmospheric turbidity factor [dimensionless] corrected by Kasten [24].

    - m is the relative optical air mass [-] calculated using the formula:

      m = (p/p0)/(sin h0ref + 0.50572 (h0ref + 6.07995)-1.6364)
      
      where :
      
      - h0ref is the corrected solar altitude h0 in degrees by the atmospheric refraction component ∆h0ref

      where : 
      
      - ∆h0ref = 0.061359 (0.1594+1.123 h0 + 0.065656 h02)/(1 + 28.9344 h0 + 277.3971 h02)
      - h0ref = h0 + ∆h0ref

      - The p/p0 component is correction for given elevation z [m]:

        p/p0 = exp (-z/8434.5)

    - δR(m) is the Rayleigh optical thickness at air mass m and is calculated according to the improved formula by Kasten as follows:

    - for m <= 20:

      δR(m) = 1/(6.6296 + 1.7513 m - 0.1202 m2 + 0.0065 m3 - 0.00013 m4)

    - for m > 20

      δR(m) = 1/(10.4 + 0.718 m)


    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    extraterrestrial_normal_irradiance_series = calculate_extraterrestrial_normal_irradiance_hofierka(
            timestamps=timestamps,
            solar_constant=solar_constant,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
            dtype=dtype,
            array_backend=array_backend,
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

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=direct_normal_irradiance_series,
        shape=timestamps.shape,
        data_model=DirectNormalIrradiance(),
        clip_to_physically_possible_limits=clip_to_physically_possible_limits,
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_normal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return DirectNormalIrradiance(
        value=direct_normal_irradiance_series,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        #
        extraterrestrial_normal_irradiance=extraterrestrial_normal_irradiance_series,
        linke_turbidity_factor_adjusted=corrected_linke_turbidity_factor_series,
        linke_turbidity_factor=linke_turbidity_factor_series,
        rayleigh_optical_thickness=rayleigh_optical_thickness_series,
        optical_air_mass=optical_air_mass_series,
        #
        solar_constant=solar_constant,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
    )
