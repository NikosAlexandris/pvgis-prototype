from pvgisprototype.log import log_function_call
from pvgisprototype.core.caching import custom_cached
from pvgisprototype import Latitude, EventHourAngle
from numpy import arccos, arctan


@log_function_call
@custom_cached
def calculate_event_hour_angle_pvis(
    latitude: Latitude,
    surface_tilt: float = 0,
    solar_declination: float = 0,
) -> EventHourAngle:
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
    hour_angle_sunrise_value = arccos(
        -arctan(latitude - surface_tilt) * arctan(solar_declination)
    )

    return EventHourAngle(
        value=hour_angle_sunrise_value,
        unit=RADIANS,
    )
