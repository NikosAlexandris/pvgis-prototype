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
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from math import isfinite
from math import pi
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype import AtmosphericRefraction
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarZenithNOAAInput
from pvgisprototype.algorithms.noaa.function_models import AdjustSolarZenithForAtmosphericRefractionNOAAInput
from pvgisprototype.algorithms.noaa.function_models import CalculateSolarZenithNOAATimeSeriesInput
from pvgisprototype.algorithms.noaa.function_models import AdjustSolarZenithForAtmosphericRefractionNOAATimeSeriesInput
from pvgisprototype import SolarZenith
from pvgisprototype import SolarAltitude
from pvgisprototype import Latitude
from pvgisprototype import SolarHourAngle
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_noaa
from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
import numpy as np


def atmospheric_refraction_for_high_solar_altitude(
    solar_altitude: SolarAltitude,  # radians
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

    return AtmosphericRefraction(value=radians(adjustment_in_degrees), unit='radians')


def atmospheric_refraction_for_near_horizon(
    solar_altitude: SolarAltitude,  # radians
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

    return AtmosphericRefraction(value=radians(adjustment_in_degrees), unit='radians')


def atmospheric_refraction_for_below_horizon(
    solar_altitude: SolarAltitude,  # radians
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

    return AtmosphericRefraction(value=radians(adjustment_in_degrees), unit='radians')


@validate_with_pydantic(AdjustSolarZenithForAtmosphericRefractionNOAAInput)
def adjust_solar_zenith_for_atmospheric_refraction(
        solar_zenith: float,  # radians
        angle_output_units: str = 'radians',
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

    solar_altitude = radians(90) - solar_zenith # in radians
    if solar_altitude <= radians(85):

        if solar_altitude > radians(5):
            function: Callable = atmospheric_refraction_functions['high_solar_altitude']
        
        elif solar_altitude > radians(-0.575):
            function = atmospheric_refraction_functions['near_horizon']
        
        else:
            function = atmospheric_refraction_functions['below_horizon']
        
        # solar zenith = 0 degrees + refraction correction.
        atmospheric_refraction_adjustment_radians = function(solar_altitude)  # in radians
        adjusted_solar_zenith = solar_zenith - atmospheric_refraction_adjustment_radians.value  # in radians
        # solar_zenith += function(solar_altitude)  # in radians

    # Reasonably increase the upper limit for the solar zenith
    # beyond π/2 radians to account for atmospheric refraction.
    # i.e. at 90.833 degrees or about π/2 + 0.0146 radians
    # which is the solar zenith angle when the center of the sun is at the horizon,
    # considering both its apparent size and atmospheric refraction.
    if not isfinite(adjusted_solar_zenith) or not 0 <= adjusted_solar_zenith <= pi + 0.0146:
        raise ValueError(f'The `solar_zenith` should be a finite number ranging in [0, {pi + 0.0146}] radians')

    solar_zenith = SolarZenith(
        value=adjusted_solar_zenith,
        unit='radians',
    )

    return solar_zenith


@validate_with_pydantic(AdjustSolarZenithForAtmosphericRefractionNOAATimeSeriesInput)
def adjust_solar_zenith_for_atmospheric_refraction_time_series(
        solar_zenith_series: np.ndarray,  # radians
        angle_output_units: str = 'radians',
    ) -> np.ndarray:
    """Adjust solar zenith for atmospheric refraction for a time series of solar zenith angles"""
    atmospheric_refraction_functions = {
        'high_solar_altitude': np.vectorize(atmospheric_refraction_for_high_solar_altitude),
        'near_horizon': np.vectorize(atmospheric_refraction_for_near_horizon),
        'below_horizon': np.vectorize(atmospheric_refraction_for_below_horizon)
    }

    solar_altitudes = np.radians(90) - solar_zenith_series  # in radians
    adjusted_solar_zeniths = np.copy(solar_zenith_series)

    mask_high = solar_altitudes > np.radians(5)
    mask_near = (solar_altitudes > np.radians(-0.575)) & ~mask_high
    mask_below = solar_altitudes <= np.radians(-0.575)

    function_high = np.vectorize(lambda x: atmospheric_refraction_for_high_solar_altitude(x).value)
    function_near = np.vectorize(lambda x: atmospheric_refraction_for_near_horizon(x).value)
    function_below = np.vectorize(lambda x: atmospheric_refraction_for_below_horizon(x).value)

    if mask_high.any():
        adjusted_solar_zeniths[mask_high] -= function_high(solar_altitudes[mask_high])
    if mask_near.any():
        adjusted_solar_zeniths[mask_near] -= function_near(solar_altitudes[mask_near])
    if mask_below.any():
        adjusted_solar_zeniths[mask_below] -= function_below(solar_altitudes[mask_below])

    if not np.all(np.isfinite(adjusted_solar_zeniths)) or not np.all((0 <= adjusted_solar_zeniths) & (adjusted_solar_zeniths <= np.pi + 0.0146)):
        raise ValueError(f'The `solar_zenith` should be a finite number ranging in [0, {np.pi + 0.0146}] radians')

    if angle_output_units == 'degrees':
        adjusted_solar_zeniths = np.degrees(adjusted_solar_zeniths)

    return adjusted_solar_zeniths


@validate_with_pydantic(CalculateSolarZenithNOAAInput)
def calculate_solar_zenith_noaa(
        latitude: Latitude,  # radians
        timestamp: datetime,
        solar_hour_angle: SolarHourAngle,
        apply_atmospheric_refraction: bool = False,
        angle_output_units: str = 'radians',
    ) -> SolarZenith:
    """Calculate the solar zenith angle (φ) in radians """
    solar_declination = calculate_solar_declination_noaa(
            timestamp=timestamp,
            angle_output_units='radians',
            )
    cosine_solar_zenith = sin(latitude.value) * sin(solar_declination.value) + cos(
        latitude.value
    ) * cos(solar_declination.value) * cos(solar_hour_angle.value)
    solar_zenith=acos(cosine_solar_zenith)
    solar_zenith = SolarZenith(
        value=solar_zenith,
        unit='radians',
    )
    if apply_atmospheric_refraction:
        solar_zenith = adjust_solar_zenith_for_atmospheric_refraction(
            solar_zenith.value,
            angle_output_units="radians",  # always in radians!
        )
    # if not isfinite(solar_zenith.value) or not 0 <= solar_zenith.value <= pi/2 + 0.0146:
    if not isfinite(solar_zenith.value) or not 0 <= solar_zenith.value <= pi + 0.0146:
        raise ValueError(f'The `solar_zenith` should be a finite number ranging in [0, {pi + 0.0146}] radians')
    solar_zenith = convert_to_degrees_if_requested(solar_zenith, angle_output_units)

    return solar_zenith


@validate_with_pydantic(CalculateSolarZenithNOAATimeSeriesInput)
def calculate_solar_zenith_time_series_noaa(
        latitude: Latitude,  # radians
        timestamps: Union[datetime, Sequence[datetime]],
        solar_hour_angle_series: Union[SolarHourAngle, Sequence[SolarHourAngle]],
        apply_atmospheric_refraction: bool = False,
        angle_output_units: str = 'radians',
) -> Union[SolarZenith, np.ndarray]:
    """ """
    solar_declination_series = calculate_solar_declination_time_series_noaa(
            timestamps=timestamps,
            angle_output_units='radians',
            )
    solar_declination_series = np.array([item.value for item in solar_declination_series])

    if isinstance(solar_hour_angle_series, SolarHourAngle):  # single SolarHourAngle
        solar_hour_angle_series = [solar_hour_angle_series]  # one-element list

    # convert to a NumPy array
    solar_hour_angle_series = np.array([item.value for item in solar_hour_angle_series])

    latitude_value = latitude.value

    cosine_solar_zenith = (
        np.sin(latitude_value) * np.sin(solar_declination_series)
        + np.cos(latitude_value) * np.cos(solar_declination_series) * np.cos(solar_hour_angle_series)
    )
    solar_zeniths = np.arccos(cosine_solar_zenith)

    if apply_atmospheric_refraction:
        solar_zeniths = adjust_solar_zenith_for_atmospheric_refraction_time_series(
            solar_zeniths, angle_output_units="radians"
        )

    if not np.all(np.isfinite(solar_zeniths)) or not np.all((0 <= solar_zeniths) & (solar_zeniths <= np.pi + 0.0146)):
        raise ValueError(f'The `solar_zenith` should be a finite number ranging in [0, {np.pi + 0.0146}] radians')

    solar_zeniths = [
        SolarZenith(value=value, unit='radians') for value in solar_zeniths
    ]
    if angle_output_units == "degrees":
        solar_zeniths = [
            convert_to_degrees_if_requested(zenith, angle_output_units)
            for zenith in solar_zeniths
        ]

    if np.isscalar(timestamps):
        return solar_zeniths[0]
    else:
        return np.array(solar_zeniths, dtype=object)
