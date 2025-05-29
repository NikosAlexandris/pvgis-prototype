"""
This Python module is part of PVGIS' API. It implements functions to calculate
the direct normal solar irradiance.

_Direct_ or _beam_ irradiance is one of the main components of solar
irradiance. It comes perpendicular from the Sun and is not scattered before it
irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _direct_ irradiance.
"""

from zoneinfo import ZoneInfo

from devtools import debug
from numpy import ndarray
from pandas import DatetimeIndex

from pvgisprototype import (
    DirectNormalFromHorizontalIrradiance,
    Latitude,
    Longitude,
)
from pvgisprototype.algorithms.hofierka.irradiance.direct.normal import (
    calculate_direct_normal_from_horizontal_irradiance_hofierka
)
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SolarPositionModel,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_radians_if_requested,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    PERIGEE_OFFSET,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.hashing import generate_hash


@log_function_call
@custom_cached
def calculate_direct_normal_from_horizontal_irradiance_series(
    direct_horizontal_irradiance: ndarray,
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex | None = None,
    timezone: ZoneInfo | None = None,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> DirectNormalFromHorizontalIrradiance:
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
    # FixMe : somehow let the angle_output_units requested by the user work !
    solar_altitude_series = model_solar_altitude_series(
        longitude=convert_float_to_radians_if_requested(longitude, RADIANS),
        latitude=convert_float_to_radians_if_requested(latitude, RADIANS),
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
    )
    direct_normal_irradiance_series = calculate_direct_normal_from_horizontal_irradiance_hofierka(
        direct_horizontal_irradiance=direct_horizontal_irradiance,
        solar_altitude_series=solar_altitude_series,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )
    direct_normal_irradiance_series.build_output(verbose, fingerprint)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_normal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return direct_normal_irradiance_series
