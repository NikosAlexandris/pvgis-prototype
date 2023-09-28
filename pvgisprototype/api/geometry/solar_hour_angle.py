from devtools import debug
from typing import Annotated
from typing import Optional
from math import pi
from math import radians
from math import acos
from math import tan
from datetime import time
from pvgisprototype import HourAngle
from pvgisprototype import HourAngleSunrise
from pvgisprototype import Latitude
from pvgisprototype import HourAngle
from pvgisprototype import HourAngleSunrise
from pvgisprototype import Latitude
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.validation.functions import CalculateHourAngleInputModel
from pvgisprototype.validation.functions import CalculateHourAngleSunriseInputModel
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours
from pvgisprototype.api.utilities.timestamp import convert_hours_to_seconds
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested


@validate_with_pydantic(CalculateHourAngleInputModel)
def calculate_hour_angle(
    solar_time: time,
    angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
):
    """Calculate the hour angle ω'

    ω = (ST / 3600 - 12) * 15 * pi / 180

    Parameters
    ----------

    solar_time : float
        The solar time (ST) is a calculation of the passage of time based on the
        position of the Sun in the sky. It is expected to be decimal hours in a
        24 hour format and measured internally in seconds. 
    
    output_units: str, optional
        Angle output units (degrees or radians).

    Returns
    -------

    Tuple(float, str)
        Tuple containg (hour_angle, units). Hour angle is the angle (ω) at any
        instant through which the earth has to turn to bring the meridian of the
        observer directly in line with the sun's rays measured in radian.

    Notes
    -----

    The hour angle ω (elsewhere symbolised with `h`) of a point on the earth’s
    surface is defined as the angle through which the earth would turn to bring
    the meridian of the point directly under the sun. The hour angle at local
    solar noon is zero, with each 360/24 or 15° of longitude equivalent to 1 h,
    afternoon hours being designated as positive. Expressed symbolically, the
    hour angle in degrees is:

        h = ±0.25 (Number of minutes from local solar noon)

    where the plus sign applies to afternoon hours and the minus sign to
    morning hours.

    The hour angle can also be obtained from the apparent solar time (AST);
    that is, the corrected local solar time:

        h = (AST - 12) * 15

    At local solar noon, AST = 12 and h = 0°. Therefore, from Eq <<(2.3)<<, the
    local solar time (LST, the time shown by our clocks at local solar noon)
    is:

        LST = 12 - ET ∓ 4 * (SL - LL)

        where:

            ET is the Equation of Time
            SL Standard Longitude
            LL Local Longitude

    Example 1

    The equation for LST at local solar noon for Nicosia, Cyprus is:

        LST = 12 - ET - 13.32 (minutes)

    Example 2

    Given the ET for March 10 (N = 69) is calculated from Eq (2.1), in which
    the factor B is obtained from Eq <<(2.2)<< as:
        
        B = 360 / 364 * (N-81) = 360 / 364 * (69- 81) = -11.87
        
        ET = 9.87 * sin(2*B) - 7.53 * cos(B) - 1.5 * sin(B) =
           = 9.87 * sin(-2 * 11.87) - 7.53 * cos(-11.87) - 1.5 * sin(-11.87)
           = -11.04min ∼ -11min

    The standard meridian for Athens is 30°E longitude.

    The apparent solar time on March 10 at 2:30 pm for the city of Athens,
    Greece (23°40′E longitude) is 

        AST = 14:30 - 4 * (30 - 23.66) - 0:11
            = 14:30 - 0:25 - 0:11 
            = 13:54 or 1:54 pm

    Additional notes:
    

    Nomenclature from [1]_

    α [°] solar altitude angle
    β [°] tilt angle
    δ [°] solar declination
    θ [°] solar incidence angle
    Φ [°] solar zenith angle
    h [°] hour angle
    L [°] local latitude
    N [-] day of the year
    z [°] solar azimuth angle
    ZS [°] surface azimuth angle
    AST Apparent Solar Time
    LST Local Standard Time
    ET Equation of Time
    SL Standard Longitude
    LL Local Longitude
    DS Daylight Saving 

    .. [1] Determination of Optimal Position of Solar Trough Collector. Available from: https://www.researchgate.net/publication/317826540_Determination_of_Optimal_Position_of_Solar_Trough_Collector [accessed Sep 06 2023].

    In PVGIS :
        hour_angle = (solar_time / 3600 - 12) * 15 * 0.0175

        which means:
        - solar time is expected in seconds
        - conversion to radians `* 0.0175` replaced by `pi / 180`

    In this function:
    """
    solar_time_decimal_hours = timestamp_to_decimal_hours(solar_time)
    hour_angle = (solar_time_decimal_hours - 12) * radians(15)
    hour_angle = HourAngle(value=hour_angle, unit='radians')
    hour_angle = convert_to_degrees_if_requested(hour_angle, angle_output_units)

    return hour_angle


@validate_with_pydantic(CalculateHourAngleSunriseInputModel)
def calculate_hour_angle_sunrise(
    latitude: Latitude,
    surface_tilt: float = 0,
    solar_declination: float = 0,
    angle_output_units: str = "radians",
) -> HourAngleSunrise:
    """Calculate the hour angle (ω) at sunrise and sunset

    Parameters
    ----------

    latitude: float
        Latitude (Φ) is the angle between the sun's rays and its projection on the
        horizontal surface measured in radians

    surface_tilt: float
        Surface tilt (or slope) (β) is the angle between the inclined surface
        (slope) and the horizontal plane.

    solar_declination: float
        Solar declination (δ) is the angle between the equator and a line drawn
        from the centre of the Earth to the centre of the sun measured in
        radians.

    Returns
    -------

    Tuple(float, str)
        Tuple containg (hour_angle, units). Hour angle (ω) is the angle at any
        instant through which the earth has to turn to bring the meridian of the
        observer directly in line with the sun's rays measured in radian.

    Notes
    -----
    Hour angle = acos(-tan(Latitude Angle-Tilt Angle)*tan(Declination Angle))

    The hour angle (ω) at sunrise and sunset measures the angular distance
    between the sun at the local solar time and the sun at solar noon.

    ω = acos(-tan(Φ-β)*tan(δ))
    """
    hour_angle_sunrise = acos(
        -tan(latitude.radians - surface_tilt.radians) * tan(solar_declination.radians)
    )
    hour_angle_sunrise = HourAngleSunrise(value=hour_angle_sunrise, unit="radians")
    hour_angle_sunrise = convert_to_degrees_if_requested(
        hour_angle_sunrise,
        angle_output_units,
    )

    return hour_angle_sunrise
