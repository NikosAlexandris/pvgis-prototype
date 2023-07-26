from .noaa_models import AdjustSolarZenithForAtmosphericRefractionNOAAInput
from .noaa_models import CalculateSolarZenithNOAAInput
from .decorators import validate_with_pydantic
from datetime import datetime
from .solar_declination import calculate_solar_declination_noaa
from math import sin
from math import cos
from math import tan
from math import acos
from math import radians
from math import degrees
from ...api.utilities.conversions import convert_to_degrees_if_requested
from math import isfinite
from math import pi
from typing import NamedTuple
from pvgisprototype.api.named_tuples import generate


def atmospheric_refraction_for_high_solar_altitude(
    solar_altitude: float,
) -> float:
    """
    Calculate the atmospheric refraction adjustment for high solar_altitudes.

    Parameters:
    tangent_solar_altitude (float): The tangent of the solar altitude angle

    Returns:
    float: The correction factor
    """
    tangent_solar_altitude = tan(solar_altitude)  # in radians
    adjustment_in_degrees = (
        58.1 / tangent_solar_altitude
        - 0.07 / (tangent_solar_altitude**3)
        + 0.000086 / (tangent_solar_altitude**5)
    ) / 3600  # 1 degree / 3600 seconds

    return radians(adjustment_in_degrees)


def atmospheric_refraction_for_near_horizon(solar_altitude: float) -> float:
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

    return radians(adjustment_in_degrees)


def atmospheric_refraction_for_below_horizon(solar_altitude: float) -> float:
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

    return radians(adjustment_in_degrees)


@validate_with_pydantic(AdjustSolarZenithForAtmosphericRefractionNOAAInput)
def adjust_solar_zenith_for_atmospheric_refraction(
        solar_zenith: float,
        angle_output_units: str = 'radians',
        ) -> NamedTuple:
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
        The solar zenith angle in degrees

    Returns
    -------
    float: The corrected solar zenith angle
    """
    atmospheric_refraction_functions: Dict[str, Callable[[float], float]] = {
        'high_solar_altitude': atmospheric_refraction_for_high_solar_altitude,
        'near_horizon': atmospheric_refraction_for_near_horizon,
        'below_horizon': atmospheric_refraction_for_below_horizon
    }

    solar_altitude = radians(90) - solar_zenith  # in radians
    if solar_altitude <= radians(85):

        if solar_altitude > radians(5):
            function: Callable = atmospheric_refraction_functions['high_solar_altitude']
        
        elif solar_altitude > radians(-0.575):
            function = atmospheric_refraction_functions['near_horizon']
        
        else:
            function = atmospheric_refraction_functions['below_horizon']
        
        # solar zenith = 0 degrees + refraction correction.
        atmospheric_refraction_adjustment_radians = function(solar_altitude)  # in radians
        solar_zenith -= atmospheric_refraction_adjustment_radians  # in radians
        # solar_zenith += function(solar_altitude)  # in radians

    # Reasonably increase the upper limit for the solar zenith
    # beyond π/2 radians to account for atmospheric refraction.
    # i.e. at 90.833 degrees or about π/2 + 0.0146 radians
    # which is the solar zenith angle when the center of the sun is at the horizon,
    # considering both its apparent size and atmospheric refraction.
    if not isfinite(solar_zenith) or not 0 <= solar_zenith <= pi + 0.0146:
        raise ValueError(f'The `solar_zenith` should be a finite number ranging in [0, {pi + 0.0146}] radians')

    solar_zenith = generate(
        'solar_zenith'.upper(),
        (solar_zenith, angle_output_units),
    )

    return solar_zenith


@validate_with_pydantic(CalculateSolarZenithNOAAInput)
def calculate_solar_zenith_noaa(
        latitude: float,
        timestamp: datetime,
        solar_hour_angle: float,
        apply_atmospheric_refraction: bool = False,
        # time_output_units: str = 'minutes',
        angle_units: str = 'radians',
        angle_output_units: str = 'radians',
        )-> NamedTuple:
    """Calculate the solar zenith angle (φ) in radians """
    solar_declination, _units = calculate_solar_declination_noaa(
            timestamp,
            angle_units,
            angle_output_units,
            )
    cosine_solar_zenith = sin(latitude) * sin(solar_declination) + cos(latitude) * cos(
        solar_declination
    ) * cos(solar_hour_angle)

    solar_zenith = generate(
        'solar_zenith'.upper(),
        (acos(cosine_solar_zenith), angle_output_units)
    )

    if apply_atmospheric_refraction:
        solar_zenith, _units = adjust_solar_zenith_for_atmospheric_refraction(
            solar_zenith,
            angle_output_units="radians",  # always in radians!
        )
    # if not isfinite(solar_zenith) or not 0 <= solar_zenith <= pi/2 + 0.0146:
    #     raise ValueError('The `solar_zenith` should be a finite number ranging in [0, π + 0.0146] radians')
    if not isfinite(solar_zenith) or not 0 <= solar_zenith <= pi + 0.0146:
        raise ValueError(f'The `solar_zenith` should be a finite number ranging in [0, {pi + 0.0146}] radians')

    # solar_zenith = convert_to_degrees_if_requested(solar_zenith, angle_output_units)
    return solar_zenith
