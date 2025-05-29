from numpy import unique, pi, cos
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import ExtraterrestrialNormalIrradiance
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
from pvgisprototype.validation.values import identify_values_out_of_range


def get_days_per_year(years):
    return 365 + ((years % 4 == 0) & ((years % 100 != 0) | (years % 400 == 0))).astype(
        int
    )


@log_function_call
@custom_cached
def calculate_extraterrestrial_normal_irradiance_hofierka(
    timestamps: DatetimeIndex | None,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
) -> ExtraterrestrialNormalIrradiance:
    """
    Calculate the normal extraterrestrial irradiance over a period of time.
    This function implements the algorithm described by Hofierka [1]_.

    Outside the atmosphere, at the mean solar distance, the direct (beam) irradiance, also known as
    the solar constant (I0), is 1367 W.m-2. The earth’s orbit is lightly eccentric and the sun-
    earth distance varies slightly across the year. Therefore a correction factor ε, to allow for
    the varying solar distance, is applied in calculation of the
    extraterrestrial irradiance `G0` normal to the solar beam [W.m-2] :

        G0 = I0 ⋅ ε (1)
    where :

        ε = 1 + 0.03344 cos (j’ - 0.048869) (2)

        where the day angle j’ is in radians :

            j’ = 2 π j/365.25 (3)

    and `j` is the day number which varies from 1 on January 1st to 365 (366) on
    December 31st.

    Parameters
    ----------
    timestamps: DatetimeIndex

    solar_constant: float

    eccentricity_phase_offset: float

    eccentricity_amplitude: float

    dtype:

    array_backend:

    verbose: int

    log: int

    Returns
    -------
    ExtraterrestrialNormalIrradiance

    Notes
    -----
    In [1]_ : G0h = G0 sin(h0)  or else : G0 horizontal = G0 ⋅ sin(solar altitude)

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    years_in_timestamps = timestamps.year
    years, indices = unique(years_in_timestamps, return_inverse=True)
    days_per_year = get_days_per_year(years).astype(dtype)
    days_in_years = days_per_year[indices]
    day_of_year_series = timestamps.dayofyear.to_numpy().astype(dtype)
    # day angle == fractional year, hence : use model_fractional_year_series()
    day_angle_series = 2 * pi * day_of_year_series / days_in_years
    distance_correction_factor_series = 1 + eccentricity_amplitude * cos(
        day_angle_series - eccentricity_phase_offset
    )
    extraterrestrial_normal_irradiance = (
        solar_constant * distance_correction_factor_series
    )

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=extraterrestrial_normal_irradiance,
        shape=timestamps.shape,
        data_model=ExtraterrestrialNormalIrradiance(),
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=extraterrestrial_normal_irradiance,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return ExtraterrestrialNormalIrradiance(
        value=extraterrestrial_normal_irradiance,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        day_of_year=day_of_year_series,
        day_angle=day_angle_series,
        solar_constant=solar_constant,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        distance_correction_factor=distance_correction_factor_series,
        quality="Not validated!",
    )
