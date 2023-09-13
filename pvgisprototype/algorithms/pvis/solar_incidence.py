import typer
from typing import Annotated
from typing import Optional
from math import sin, cos, acos
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype import SolarIncidence
from pvgisprototype import Latitude
from pvgisprototype.validation.functions import CalculateSolarIncidenceInputModel


@validate_with_pydantic(CalculateSolarIncidenceInputModel)
def calculate_solar_incidence(
        latitude: Latitude,
        solar_declination: float = 0,
        surface_tilt: float = 0,
        surface_orientation: float = 180,
        hour_angle: float = None,
        angle_output_units: str = 'radians',
    ) -> SolarIncidence:
    """Calculate the angle of incidence (θ) between the direction of the sun
    ray and the line normal to the surface measured in radian.

    θ =
    acos(
         sin(Φ)
         * (
           sin(δ) * cos(β) + cos(δ) * cos(γ) * cos(ω) * sin(β)
           )
         + cos(Φ) * (cos(δ) * cos(ω) * cos(β) - sin(δ) * cos(γ) * sin(β))
         + cos(δ)
         * sin(γ)
         * sin(ω)
         * sin(β)
        )

    Parameters
    ----------

    latitude: float
        Latitude is the angle (Φ) between the sun's rays and its projection on
        the horizontal surface measured in radian.

    solar_declination: flot
        Solar declination is the angle (δ) between the equator and a line drawn
        from the centre of the Earth to the centre of the sun measured in
        radian.

    surface_tilt: float 
        Surface tilt or slope is the angle (β) between the inclined slope and
        the horizontal plane measured in radian.

    surface_orientiation: float
        Surface orientation or azimuth is the angle (γ) in the horizontal plane
        between the line due south and the horizontal projection of the normal
        to the inclined plane surface measured in radian.

    hour_angle: float
        Hour angle is the angle (ω) at any instant through which the earth has
        to turn to bring the meridian of the observer directly in line with the
        sun's rays measured in radian.

    Returns
    -------

    solar_incidence: float
        The angle of incidence (θ) is the angle between the direction of the
        sun ray and the line normal to the surface measured in radian.
    """
    solar_incidence = acos(
        sin(latitude.value)
        * (
            sin(solar_declination.value)
            * cos(surface_tilt.value)
            + cos(solar_declination.value)
            * cos(surface_orientation.value)
            * cos(hour_angle)
            * sin(surface_tilt.value)
        )
        + cos(latitude.value)
        * (
            cos(solar_declination.value)
            * cos(hour_angle)
            * cos(surface_tilt.value)
            - sin(solar_declination.value)
            * cos(surface_orientation.value)
            * sin(surface_tilt.value)
        )
        + cos(solar_declination.value)
        * sin(surface_orientation.value)
        * sin(hour_angle)
        * sin(surface_tilt.value)
    )
    return SolarIncidence(value=solar_incidence, unit=angle_output_units)
