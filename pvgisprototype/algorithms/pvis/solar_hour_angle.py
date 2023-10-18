from devtools import debug
import typer
from datetime import datetime
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype import SolarHourAngle
from pvgisprototype import SolarHourAngle
from pvgisprototype import HourAngleSunrise
from pvgisprototype import Latitude
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarHourAnglePVISInputModel
from pvgisprototype.validation.functions import CalculateHourAngleSunrisePVISInputModel
from pvgisprototype.validation.functions import CalculateHourAngleSunrisePVISInputModel
from pvgisprototype.api.utilities.timestamp import timestamp_to_minutes
from math import pi


# @validate_with_pydantic(CalculateSolarHourAnglePVISInputModel)
def calculate_solar_hour_angle_pvis(
    solar_time:datetime,
)-> SolarHourAngle:
    """Calculate the hour angle ω'

    ω = (ST / 3600 - 12) * 15 * pi / 180

    Parameters
    ----------

    solar_time: float
        The solar time (ST) is a calculation of the passage of time based on the
        position of the Sun in the sky. It is expected to be decimal hours in a
        24 hour format and measured internally in seconds. 

    Returns
    --------

    hour_angle: float
        The solar hour angle (ω) is the angle at any instant through which the
        earth has to turn to bring the meridian of the observer directly in
        line with the sun's rays measured in radian.

    Notes
    -----
    If not mistaken, in PVGIS' C source code, the conversion function is:

        hour_angle = (solar_time / 3600 - 12) * 15 * 0.0175

        where the solar time was given in seconds.
    """
    true_solar_time_minutes = timestamp_to_minutes(solar_time)
    hour_angle = (true_solar_time_minutes / 60 - 12) * 15 * pi / 180
    hour_angle = SolarHourAngle(value=hour_angle, unit='radians')
    hour_angle = SolarHourAngle(value=hour_angle, unit='radians')

    return hour_angle


@validate_with_pydantic(CalculateHourAngleSunrisePVISInputModel)
@validate_with_pydantic(CalculateHourAngleSunrisePVISInputModel)
def calculate_hour_angle_sunrise(  # rename to: calculate_event_hour_angle
        latitude: Latitude,
        surface_tilt: float = 0,
        solar_declination: float = 0,
        # angle_output_units: str = 'radians',
        # angle_output_units: str = 'radians',
    ) -> HourAngleSunrise:
    """Calculate the hour angle (ω) at sunrise and sunset

    Hour angle = acos(-tan(Latitude Angle-Tilt Angle)*tan(Declination Angle))

    The hour angle (ω) at sunrise and sunset measures the angular distance
    between the sun at the local solar time and the sun at solar noon.

    ω = acos(-tan(Φ-β)*tan(δ))

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
    hour_angle_sunrise: float
        Hour angle (ω) is the angle at any instant through which the earth has
        to turn to bring the meridian of the observer directly in line with the
        sun's rays measured in radian.
    """
    hour_angle_sunrise_value = acos(
            -tan(
                latitude - surface_tilt
                )
            *tan(solar_declination)
            )
    hour_angle_sunrise = HourAngleSunrise(
        value=hour_angle_sunrise_value,
        unit='radians',
    )
    hour_angle_sunrise = convert_to_degrees_if_requested(
            hour_angle_sunrise,
            angle_output_units,
            )
    return hour_angle_sunrise


if __name__ == "__main__":
    typer.run(main)
