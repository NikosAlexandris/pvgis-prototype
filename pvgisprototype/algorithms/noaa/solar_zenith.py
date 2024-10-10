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
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    RADIANS,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.validation.functions import validate_with_pydantic


def atmospheric_refraction_adjustment(
    solar_altitude: np.ndarray,  # radians
    dtype: str = "float64"
) -> np.ndarray:
    """
    Vectorized calculation of atmospheric refraction adjustment for different solar altitudes.
    Applies different formulas based on the solar altitude angle.
    """
    tangent_solar_altitude = np.tan(solar_altitude)
    
    # Conditions
    mask_high = solar_altitude > np.radians(5, dtype=dtype)
    mask_near = (solar_altitude > np.radians(-0.575, dtype=dtype)) & ~mask_high
    mask_below = solar_altitude <= np.radians(-0.575, dtype=dtype)

    # High solar altitude adjustment
    adjustment_high = (
        58.1 / tangent_solar_altitude
        - 0.07 / (tangent_solar_altitude**3)
        + 0.000086 / (tangent_solar_altitude**5)
    ) / 3600  # 1 degree / 3600 seconds

    # Near horizon adjustment
    solar_altitude_deg = np.degrees(solar_altitude)
    adjustment_near = (
        1735
        + solar_altitude_deg
        * (
            -518.2
            + solar_altitude_deg
            * (103.4 + solar_altitude_deg * (-12.79 + solar_altitude_deg * 0.711))
        )
    ) / 3600  # 1 degree / 3600 seconds

    # Below horizon adjustment
    adjustment_below = (-20.774 / tangent_solar_altitude) / 3600  # 1 degree / 3600 seconds

    # Initialize adjustment array
    adjustment = np.zeros_like(solar_altitude, dtype=dtype)

    # Apply adjustments based on conditions
    adjustment[mask_high] = np.radians(adjustment_high[mask_high])
    adjustment[mask_near] = np.radians(adjustment_near[mask_near])
    adjustment[mask_below] = np.radians(adjustment_below[mask_below])

    return adjustment

@validate_with_pydantic(AdjustSolarZenithForAtmosphericRefractionTimeSeriesNOAAInput)
def adjust_solar_zenith_for_atmospheric_refraction_time_series(
    solar_zenith_series: SolarZenith,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
    validate_output:bool = VALIDATE_OUTPUT_DEFAULT
) -> SolarZenith:
    """Adjust solar zenith for atmospheric refraction for a time series of solar zenith angles"""
    # Mask
    solar_altitude_series_array = (
        np.radians(90, dtype=dtype) - solar_zenith_series.radians
    )  # in radians

    # Adjust using vectorized operations
    adjustment = atmospheric_refraction_adjustment(solar_altitude_series_array, dtype=dtype)

    adjusted_solar_zenith_series_array = solar_zenith_series.radians - adjustment

    # Validate
    '''
    if not np.all(np.isfinite(adjusted_solar_zenith_series_array)) or not np.all(
        (SolarZenith().min_radians <= adjusted_solar_zenith_series_array)
        & (adjusted_solar_zenith_series_array <= SolarZenith().max_radians)
    ):
        raise ValueError(
            f"The `adjusted_solar_zenith` should be a finite number ranging in [{SolarZenith().min_radians}, {SolarZenith().max_radians}] radians"
        )
    '''
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
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> SolarZenith:
    """Calculate the solar zenith angle for a location over a time series"""
    solar_declination_series = calculate_solar_declination_series_noaa(
        timestamps=timestamps,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        validate_output=validate_output,
    )
    solar_hour_angle_series = calculate_solar_hour_angle_series_noaa(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        validate_output=validate_output,
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
    if validate_output:
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
