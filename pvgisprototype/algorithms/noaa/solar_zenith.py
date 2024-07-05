from math import cos, degrees, radians, sin, tan
from zoneinfo import ZoneInfo

import numpy as np
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import (
    AtmosphericRefraction,
    Latitude,
    Longitude,
    SolarAltitude,
    SolarZenith,
)
from pvgisprototype.algorithms.noaa.function_models import (
    AdjustSolarZenithForAtmosphericRefractionTimeSeriesNOAAInput,
    CalculateSolarZenithTimeSeriesNOAAInput,
)
from pvgisprototype.algorithms.noaa.solar_declination import (
    calculate_solar_declination_series_noaa,
)
from pvgisprototype.algorithms.noaa.solar_hour_angle import (
    calculate_solar_hour_angle_series_noaa,
)
from pvgisprototype.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    RADIANS,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.functions import validate_with_pydantic


def atmospheric_refraction_for_high_solar_altitude(
    solar_altitude: SolarAltitude,  # radians
    verbose: int = 0,
) -> AtmosphericRefraction:
    """
    Calculate the atmospheric refraction adjustment for high solar_altitudes.

    Parameters:
    tangent_solar_altitude (float): The tangent of the solar altitude angle

    Returns:
    AtmosphericRefraction: The correction factor
    """
    tangent_solar_altitude = tan(solar_altitude)  # in radians
    adjustment_in_degrees = (
        58.1 / tangent_solar_altitude
        - 0.07 / (tangent_solar_altitude**3)
        + 0.000086 / (tangent_solar_altitude**5)
    ) / 3600  # 1 degree / 3600 seconds

    if verbose == 3:
        debug(locals())

    return AtmosphericRefraction(value=radians(adjustment_in_degrees), unit=RADIANS)


def atmospheric_refraction_for_near_horizon(
    solar_altitude: SolarAltitude,  # radians
    verbose: int = 0,
) -> AtmosphericRefraction:
    """
    Calculate the atmospheric refraction adjusment for near horizon.

    Parameters:
    solar_altitude (float): The solar solar_altitude angle

    Returns:
    float: The adjustment factor
    """
    solar_altitude = degrees(solar_altitude)
    adjustment_in_degrees = (
        1735
        + solar_altitude
        * (
            -518.2
            + solar_altitude
            * (103.4 + solar_altitude * (-12.79 + solar_altitude * 0.711))
        )
    ) / 3600  # 1 degree / 3600 seconds

    if verbose == 3:
        debug(locals())

    return AtmosphericRefraction(value=radians(adjustment_in_degrees), unit=RADIANS)


def atmospheric_refraction_for_below_horizon(
    solar_altitude: SolarAltitude,  # radians
    verbose: int = 0,
) -> AtmosphericRefraction:
    """
    Calculate the atmospheric refraction adjustment for below horizon.

    Parameters:
    tangent_solar_altitude (float): The tangent of the solar altitude angle

    Returns:
    float: The correction factor
    """
    tangent_solar_altitude = tan(solar_altitude)  # in radians
    adjustment_in_degrees = (
        -20.774 / tangent_solar_altitude
    ) / 3600  # 1 degree / 3600 seconds

    if verbose == 3:
        debug(locals())

    return AtmosphericRefraction(value=radians(adjustment_in_degrees), unit=RADIANS)


@validate_with_pydantic(AdjustSolarZenithForAtmosphericRefractionTimeSeriesNOAAInput)
def adjust_solar_zenith_for_atmospheric_refraction_time_series(
    solar_zenith_series: SolarZenith,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> SolarZenith:
    """Adjust solar zenith for atmospheric refraction for a time series of solar zenith angles"""
    # Mask
    solar_altitude_series_array = (
        np.radians(90, dtype=dtype) - solar_zenith_series.radians
    )  # in radians
    mask_high = solar_altitude_series_array > np.radians(5, dtype=dtype)
    mask_near = (
        solar_altitude_series_array > np.radians(-0.575, dtype=dtype)
    ) & ~mask_high
    mask_below = solar_altitude_series_array <= np.radians(-0.575, dtype=dtype)

    # Adjust
    function_high = np.vectorize(
        lambda x: atmospheric_refraction_for_high_solar_altitude(x).value
    )
    function_near = np.vectorize(
        lambda x: atmospheric_refraction_for_near_horizon(x).value
    )
    function_below = np.vectorize(
        lambda x: atmospheric_refraction_for_below_horizon(x).value
    )

    adjusted_solar_zenith_series_array = np.copy(solar_zenith_series.radians)
    if mask_high.any():
        adjusted_solar_zenith_series_array[mask_high] -= function_high(
            solar_altitude_series_array[mask_high]
        )
    if mask_near.any():
        adjusted_solar_zenith_series_array[mask_near] -= function_near(
            solar_altitude_series_array[mask_near]
        )
    if mask_below.any():
        adjusted_solar_zenith_series_array[mask_below] -= function_below(
            solar_altitude_series_array[mask_below]
        )

    # Validate
    if not np.all(np.isfinite(adjusted_solar_zenith_series_array)) or not np.all(
        (SolarZenith().min_radians <= adjusted_solar_zenith_series_array)
        & (adjusted_solar_zenith_series_array <= SolarZenith().max_radians)
    ):
        raise ValueError(
            f"The `adjusted_solar_zenith` should be a finite number ranging in [{SolarZenith().min_radians}, {SolarZenith().max_radians}] radians"
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return SolarZenith(
        value=adjusted_solar_zenith_series_array,
        unit=RADIANS,
        position_algorithm=solar_zenith_series.position_algorithm,
        timing_algorithm=solar_zenith_series.timing_algorithm,
    )


@log_function_call
@custom_cached
@validate_with_pydantic(CalculateSolarZenithTimeSeriesNOAAInput)
def calculate_solar_zenith_series_noaa(
    longitude: Longitude,
    latitude: Latitude,  # radians
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    # solar_hour_angle_series: SolarHourAngle,
    apply_atmospheric_refraction: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> SolarZenith:
    """Calculate the solar zenith angle for a location over a time series"""
    solar_declination_series = calculate_solar_declination_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
    )
    solar_hour_angle_series = calculate_solar_hour_angle_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    cosine_solar_zenith = sin(latitude.radians) * np.sin(
        solar_declination_series.radians
    ) + cos(latitude.radians) * np.cos(solar_declination_series.radians) * np.cos(
        solar_hour_angle_series.radians
    )
    solar_zenith_series = SolarZenith(
        value=np.arccos(cosine_solar_zenith),  # Important !
        unit=RADIANS,
        position_algorithm=solar_declination_series.position_algorithm,
        timing_algorithm=solar_hour_angle_series.timing_algorithm,
    )
    if apply_atmospheric_refraction:
        solar_zenith_series = (
            adjust_solar_zenith_for_atmospheric_refraction_time_series(
                solar_zenith_series,
            )
        )

    if not np.all(np.isfinite(solar_zenith_series.radians)) or not np.all(
        (SolarZenith().min_radians <= solar_zenith_series.radians)
        & (solar_zenith_series.radians <= SolarZenith().max_radians)
    ):
        raise ValueError(
            f"Solar zenith values should be finite numbers and range in [{SolarZenith().min_radians}, {SolarZenith().max_radians}] radians"
        )

    log_data_fingerprint(
        data=solar_zenith_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return solar_zenith_series  # This is a SolarZenith data class !
