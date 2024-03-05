from devtools import debug
from typing import Union
from typing import Sequence
from datetime import datetime
from math import sin
from math import cos
from math import tan
from math import acos
from math import radians
from math import degrees
from pvgisprototype.api.utilities.conversions import convert_series_to_degrees_if_requested
from math import isfinite
from math import pi
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype import AtmosphericRefraction
from pvgisprototype.validation.functions import CalculateSolarZenithNOAAInput
from pvgisprototype.validation.functions import CalculateSolarZenithNOAAInput
from pvgisprototype.algorithms.noaa.function_models import AdjustSolarZenithForAtmosphericRefractionNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarZenithTimeSeriesNOAAInput
from pvgisprototype.algorithms.noaa.function_models import AdjustSolarZenithForAtmosphericRefractionTimeSeriesNOAAInput
from pvgisprototype.algorithms.noaa.parameter_models import SolarZenithSeriesModel
from pvgisprototype import SolarZenith
from pvgisprototype import SolarAltitude
from pvgisprototype import Latitude
from pvgisprototype import SolarHourAngle
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_noaa
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
import numpy as np
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from cachetools import cached
from pvgisprototype.algorithms.caching import custom_hashkey


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


@validate_with_pydantic(AdjustSolarZenithForAtmosphericRefractionNOAAInput)
def adjust_solar_zenith_for_atmospheric_refraction(
    solar_zenith: SolarZenith,  # radians
    verbose: int = 0,
) -> SolarZenith:
    """Adjust solar zenith for atmospheric refraction

    The effects of the atmosphere vary with atmospheric pressure, humidity, and
    other variables. Therefore, the solar position calculations presented here
    are approximate. Errors in sunrise and sunset times can be expected to
    increase the further away you are from the equator, because the sun rises
    and sets at a very shallow angle. Small variations in the atmosphere can
    have a larger effect.

    Parameters
    ----------
    solar_zenith: float
        The solar zenith angle in radians

    Returns
    -------
    float: The corrected solar zenith angle
    """
    atmospheric_refraction_functions: Dict[str, Callable[[float], float]] = {
        'high_solar_altitude': atmospheric_refraction_for_high_solar_altitude,
        'near_horizon': atmospheric_refraction_for_near_horizon,
        'below_horizon': atmospheric_refraction_for_below_horizon
    }

    solar_altitude = radians(90) - solar_zenith.radians
    if solar_altitude <= radians(85):

        if solar_altitude > radians(5):
            function: Callable = atmospheric_refraction_functions['high_solar_altitude']
        
        elif solar_altitude > radians(-0.575):
            function = atmospheric_refraction_functions['near_horizon']
        
        else:
            function = atmospheric_refraction_functions['below_horizon']
        
        # solar zenith = 0 degrees + refraction correction.
        atmospheric_refraction_adjustment_radians = function(solar_altitude)  # in radians
        adjusted_solar_zenith = solar_zenith.radians - atmospheric_refraction_adjustment_radians.radians

    solar_zenith = SolarZenith(
        value=adjusted_solar_zenith,
        unit=RADIANS,
    )

    # Reasonably increase the upper limit for the solar zenith
    # beyond π/2 radians to account for atmospheric refraction.
    # i.e. at 90.833 degrees or about π/2 + 0.0146 radians
    # which is the solar zenith angle when the center of the sun is at the horizon,
    # considering both its apparent size and atmospheric refraction.
    if (
        not isfinite(solar_zenith.degrees)
        or not solar_zenith.min_degrees <= solar_zenith.degrees <= solar_zenith.max_degrees
    ):
        raise ValueError(
            f"The calculated solar zenith angle {solar_zenith.degrees} is out of the expected range\
            [{solar_zenith.min_degrees}, {solar_zenith.max_degrees}] degrees"
        )

    if verbose > 5:
        debug(locals())

    return solar_zenith


@validate_with_pydantic(AdjustSolarZenithForAtmosphericRefractionTimeSeriesNOAAInput)
def adjust_solar_zenith_for_atmospheric_refraction_time_series(
        solar_zenith_series: SolarZenith,
        verbose: int = 0,
    ) -> SolarZenith:
    """Adjust solar zenith for atmospheric refraction for a time series of solar zenith angles"""
    # Mask 
    solar_altitude_series_array = np.radians(90) - solar_zenith_series.radians  # in radians
    mask_high = solar_altitude_series_array > np.radians(5)
    mask_near = (solar_altitude_series_array > np.radians(-0.575)) & ~mask_high
    mask_below = solar_altitude_series_array <= np.radians(-0.575)

    # Adjust
    function_high = np.vectorize(lambda x: atmospheric_refraction_for_high_solar_altitude(x).value)
    function_near = np.vectorize(lambda x: atmospheric_refraction_for_near_horizon(x).value)
    function_below = np.vectorize(lambda x: atmospheric_refraction_for_below_horizon(x).value)

    adjusted_solar_zenith_series_array = np.copy(solar_zenith_series.radians)
    if mask_high.any():
        adjusted_solar_zenith_series_array[mask_high] -= function_high(solar_altitude_series_array[mask_high])
    if mask_near.any():
        adjusted_solar_zenith_series_array[mask_near] -= function_near(solar_altitude_series_array[mask_near])
    if mask_below.any():
        adjusted_solar_zenith_series_array[mask_below] -= function_below(solar_altitude_series_array[mask_below])

    # Validate
    if not np.all(np.isfinite(adjusted_solar_zenith_series_array)) or not np.all((SolarZenith().min_radians <= adjusted_solar_zenith_series_array) & (adjusted_solar_zenith_series_array <= SolarZenith().max_radians)):
        raise ValueError(f'The `adjusted_solar_zenith` should be a finite number ranging in [{SolarZenith().min_radians}, {SolarZenith().max_radians}] radians')

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return SolarZenith(
        value=adjusted_solar_zenith_series_array,
        unit=RADIANS,
        position_algorithm=solar_zenith_series.position_algorithm,
        timing_algorithm=solar_zenith_series.timing_algorithm
    )


@validate_with_pydantic(CalculateSolarZenithNOAAInput)
def calculate_solar_zenith_noaa(
    latitude: Latitude,  # radians
    timestamp: datetime,
    solar_hour_angle: SolarHourAngle,
    apply_atmospheric_refraction: bool = True,
    verbose: int = 0,
) -> SolarZenith:
    """Calculate the solar zenith angle (φ) in radians """
    solar_declination = calculate_solar_declination_noaa(
        timestamp=timestamp,
    )
    cosine_solar_zenith = sin(latitude.radians) * sin(solar_declination.radians) + cos(
        latitude.radians
    ) * cos(solar_declination.radians) * cos(solar_hour_angle.radians)
    solar_zenith = acos(cosine_solar_zenith)
    if apply_atmospheric_refraction:
        solar_zenith = adjust_solar_zenith_for_atmospheric_refraction(
            solar_zenith,
        )  # always in radians!
    if (
        not isfinite(solar_zenith.degrees)
        or not solar_zenith.min_degrees <= solar_zenith.degrees <= solar_zenith.max_degrees
    ):
        raise ValueError(
            f"The calculated solar zenith angle {solar_zenith.degrees} is out of the expected range\
            [{solar_zenith.min_degrees}, {solar_zenith.max_degrees}] degrees"
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return SolarZenith(
        value=solar_zenith,
        unit=RADIANS,
        position_algorithm='NOAA',
        timing_algorithm='NOAA',
    )


# @cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateSolarZenithTimeSeriesNOAAInput)
def calculate_solar_zenith_time_series_noaa(
        latitude: Latitude,  # radians
        timestamps: Union[datetime, Sequence[datetime]],
        solar_hour_angle_series: SolarHourAngle,
        apply_atmospheric_refraction: bool = False,
        verbose: int = 0,
    ) -> SolarZenith:
    """Calculate the solar zenith angle for a location over a time series"""
    solar_declination_series = calculate_solar_declination_time_series_noaa(
            timestamps=timestamps,
            )
    cosine_solar_zenith = (
        np.sin(latitude.radians) * np.sin(solar_declination_series.radians)
        + np.cos(latitude.radians) * np.cos(solar_declination_series.radians) * np.cos(solar_hour_angle_series.radians)
    )
    solar_zenith_series = np.arccos(cosine_solar_zenith)

    # from pvgisprototype.validation.hashing import generate_hash
    # solar_zenith_series_hash = generate_hash(solar_zenith_series)
    # print(
    #     "SolarZenith : calculate_solar_zenith_time_series_noaa() |",
    #     f"Data Type : [bold]{solar_zenith_series.dtype}[/bold] |",
    #     f"Output Hash : [code]{solar_zenith_series_hash}[/code]",
    # )

    if apply_atmospheric_refraction:
        solar_zenith_series = (
            adjust_solar_zenith_for_atmospheric_refraction_time_series(
                SolarZenith(
                    value=solar_zenith_series,
                    unit=RADIANS,
                    timing_algorithm="NOAA",
                    position_algorithm="NOAA",
                )
            )
        )

    if not np.all(np.isfinite(solar_zenith_series.radians)) or not np.all(
        (SolarZenith().min_radians <= solar_zenith_series.radians)
        & (solar_zenith_series.radians <= SolarZenith().max_radians)
    ):
        raise ValueError(
            f"Solar zenith values should be finite numbers and range in [{SolarZenith().min_radians}, {SolarZenith().max_radians}] radians"
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    # return SolarZenith(
    #     value=solar_zenith_series,
    #     unit=RADIANS,
    #     position_algorithm='NOAA',
    #     timing_algorithm='NOAA',
    # )
    return solar_zenith_series
