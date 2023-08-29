from datetime import datetime
from zoneinfo import ZoneInfo
import typer
from typing import Annotated
from typing import List
from typing import Optional
from math import sin, cos, acos
from math import asin
from math import atan
from ...api.utilities.timestamp import now_utc_datetimezone
from ..noaa.solar_hour_angle import calculate_solar_hour_angle_noaa
from ...api.geometry.solar_declination import calculate_solar_declination_pvis
from ...api.utilities.timestamp import ctx_convert_to_timezone
from ...api.utilities.conversions import convert_to_radians
from ...api.utilities.timestamp import ctx_attach_requested_timezone

from pvgisprototype.api.data_classes import RelativeLongitude
from pvgisprototype.api.data_classes import SolarIncidence
from pvgisprototype.api.data_classes import HorizonHeight
from pvgisprototype.api.data_classes import Longitude
from pvgisprototype.api.data_classes import Latitude

from pvgisprototype.api.decorators import validate_with_pydantic
from pvgisprototype.api.function_models import CalculateRelativeLongitudeInputModel
from pvgisprototype.api.function_models import CalculateSolarIncidenceJencoInputModel


NO_SOLAR_INCIDENCE = 0  # Solar incidence when shadow is detected


@validate_with_pydantic(CalculateRelativeLongitudeInputModel, expand_args=True)
def calculate_relative_longitude(
        latitude: Latitude,
        surface_tilt: float = 0,
        surface_orientation: float = 0,
        angle_output_units: str = 'radians',
    ) -> RelativeLongitude:
    """
    """
    # tangent_relative_longitude = -(
    #             sin(surface_tilt)
    #             * sin(surface_orientation)
    #         ) / (
    #             sin(latitude)
    #             * sin(surface_tilt)
    #             * cos(surface_orientation)
    #             + cos(latitude)
    #             * cos(surface_tilt)
    #         )

    tangent_relative_longitude_numerator = -(
        sin(surface_tilt.value)
        * sin(surface_orientation.value)
    )

    tangent_relative_longitude_denominator = (
            sin(latitude.value)
        * sin(surface_tilt.value)
        * cos(surface_orientation.value)
        + cos(latitude.value)
        * cos(surface_tilt.value)
    )
    
    tangent_relative_longitude = (
        tangent_relative_longitude_numerator /
        tangent_relative_longitude_denominator
    )

    relative_longitude = RelativeLongitude(
        value=atan(tangent_relative_longitude),
        unit=angle_output_units,
    )
    return relative_longitude


@validate_with_pydantic(CalculateSolarIncidenceJencoInputModel, expand_args=True)
def calculate_solar_incidence_jenco(
        longitude: Longitude,
        latitude: Latitude,
        timestamp: datetime,
        timezone: ZoneInfo = None,
        random_time: bool = False,
        hour_angle: float = None,
        surface_tilt: float = None,
        surface_orientation: float = None,
        shadow_indicator: Path = None,
        horizon_heights: Optional[List[float]] = None,
        horizon_interval: Optional[float] = None,
        days_in_a_year: float = 365.25,
        eccentricity_correction_factor: float = 0.03344,
        perigee_offset: float = 0.048869,
        time_output_units: str = 'minutes',
        angle_units: str = 'radians',
        angle_output_units: str = 'radians',
        verbose: bool = False,
    ) -> SolarIncidence:
    """Calculate the solar incidence based on sun's position and surface geometry.

    Parameters
    ----------
    hour_angle : float
        Solar hour angle in radians
    longitude : float
        Longitude in degrees
    latitude : float
        Latitude in degrees
    surface_tilt : float
        Tilt of the surface in degrees
    surface_orientation : float
        Orientation of the surface (azimuth angle in degrees)

    Returns
    -------
    float
        Solar incidence angle.

    Notes
    -----
        tg(λ') = - (sin(γN) * sin(AN)) / (sin(ϕ) * sin(γN) * cos(AN) + cos(ϕ) * cos(γN))
        sin(ϕ') = - cos(ϕ) * sin(γN) * cos(AN) + sin(ϕ) * cos(γN)
        C'31 = cos ϕ' cos δ
        C'33 = sin ϕ' sin δ

    """
    sine_relative_inclined_latitude = - (
        cos(latitude.value)
        * sin(surface_tilt.value)
        * cos(surface_orientation.value)
        + sin(latitude.value)
        * cos(surface_tilt.value)
    )
    relative_inclined_latitude = asin(sine_relative_inclined_latitude)
    solar_declination = calculate_solar_declination_pvis(
        timestamp,
        timezone,
        days_in_a_year,
        eccentricity_correction_factor,
        perigee_offset,
        angle_output_units,
        )
    c_inclined_31 = cos(relative_inclined_latitude) * cos(solar_declination.value)
    c_inclined_33 = sine_relative_inclined_latitude * sin(solar_declination.value)
    
    hour_angle = calculate_solar_hour_angle_noaa(
        longitude,
        timestamp,
        timezone,
        time_output_units,
        angle_output_units,
    )
    relative_longitude = calculate_relative_longitude(
        latitude,
        surface_tilt,
        surface_orientation
    )
    
    sine_solar_incidence = (
        c_inclined_31 * cos(hour_angle.value - relative_longitude.value) + c_inclined_33
    )

    solar_incidence = SolarIncidence(
        value=asin(sine_solar_incidence),
        unit=angle_output_units
    )
    return solar_incidence


# @validate_with_pydantic()
def interpolate_horizon_height(
    solar_azimuth: float,
    horizon_heights: List[float],
    horizon_interval: float,
) -> HorizonHeight:
    """Interpolate the height of the horizon at the sun's azimuth angle.

    Parameters
    ----------
    solar_azimuth : float
        The azimuth angle of the sun.
    horizon_heights : list of float
        List of horizon height values.
    horizon_interval : float
        Interval between successive horizon data points.

    Returns
    -------
    float
        The interpolated horizon height.
    """
    position_in_interval = solar_azimuth / horizon_interval
    position_before = int(position_in_interval)
    position_after = position_before + 1

    # Handle wrap around
    position_after = 0 if position_after == len(horizon_heights) else position_after

    # Interpolate the horizon height (or weighted average)
    horizon_height = (
        (1 - (position_in_interval - position_before))
        * horizon_heights[position_before] 
        + (position_in_interval - position_before)
        * horizon_heights[position_after]
    )

    return HorizonHeight(horizon_height, 'meters')                          # FIXME: Is it meters?


def is_surface_in_shade(
    solar_altitude: float,
    solar_azimuth: float,
    shadow_indicator: Path = None,
    horizon_heights: Optional[List[float]] = None,
    horizon_interval: Optional[float] = None,
) -> bool:
    """Check whether the solar surface is in shade based on shadow and horizon data.

    Parameters
    ----------
    shadow_indicator : int, optional
        Shadow data indicating presence of shadow, by default None.
    solar_altitude : float
        The altitude of the sun.
    solar_azimuth : float
        The azimuth angle of the sun.
    horizon_heights : list of float, optional
        List of horizon height values, by default None.
    horizon_interval : float, optional
        Interval between successive horizon data points, by default None.

    Returns
    -------
    bool
        True if the solar surface is in shade, otherwise False.
    """
    if shadow_indicator is not None and bool(shadow_indicator):
        return True

    if horizon_heights is not None:
        horizon_height = interpolate_horizon_height(solar_azimuth, horizon_heights, horizon_interval)
        if horizon_height > solar_altitude:
            return True
    
    return False
