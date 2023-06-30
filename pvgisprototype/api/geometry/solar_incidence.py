import typer
from typing import Annotated
from typing import Optional
from math import sin, cos, acos
from ..utilities.conversions import convert_to_radians
from ..utilities.conversions import convert_to_degrees_if_requested


def calculate_solar_incidence(
        latitude: Annotated[Optional[float], typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        solar_declination: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        surface_tilt: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        surface_orientation: Annotated[Optional[float], typer.Argument(
            min=0, max=360)] = 180,
        hour_angle: Annotated[Optional[float], typer.Argument(
            min=0, max=1)] = None,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ) -> float:
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
        sin(latitude) * (sin(solar_declination) * cos(surface_slope) +
                         cos(solar_declination) * cos(surface_azimuth) *
                         cos(hour_angle) * sin(surface_slope)) +
        cos(latitude) * (cos(solar_declination) * cos(hour_angle) * cos(surface_slope) -
                         sin(solar_declination) * cos(surface_azimuth) *
                         sin(surface_slope)) +
        cos(solar_declination) * sin(surface_azimuth) * sin(hour_angle) * sin(surface_slope)
    )
    return solar_incidence
