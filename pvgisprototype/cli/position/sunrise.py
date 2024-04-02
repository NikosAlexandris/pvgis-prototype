from typing import Annotated
from typing import Optional

from pvgisprototype import Latitude

from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.position import typer_argument_solar_declination
from pvgisprototype.cli.typer.position import typer_argument_surface_tilt
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.verbosity import typer_option_verbose

from pvgisprototype.api.position.hour_angle import calculate_solar_hour_angle
from pvgisprototype.cli.print import print_hour_angle_table_2

from pvgisprototype.constants import RADIANS, DEGREES
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT

from pvgisprototype.api.position.hour_angle import calculate_event_hour_angle
from pvgisprototype import SurfaceTilt
from pvgisprototype import SolarDeclination


def sunrise(
    latitude: Annotated[float, typer_argument_latitude],
    solar_declination: Annotated[Optional[float], typer_argument_solar_declination] = 45,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the hour angle 'ω = (ST / 3600 - 12) * 15 * π / 180'

    The hour angle (ω) is the angle at any instant through which the earth has
    to turn to bring the meridian of the observer directly in line with the
    sun's rays measured in radian. In other words, it is a measure of time,
    expressed in angular measurement, usually degrees, from solar noon. It
    increases by 15° per hour, negative before solar noon and positive after
    solar noon.
    """
    latitude = Latitude(value=latitude, unit=RADIANS)
    hour_angle = calculate_event_hour_angle(
        latitude=latitude,
        surface_tilt=surface_tilt,
        solar_declination=solar_declination,
    )
    surface_tilt = SurfaceTilt(value=surface_tilt, unit=RADIANS)
    solar_declination = SolarDeclination(value=solar_declination, unit=RADIANS)

    from pvgisprototype.cli.print import print_hour_angle_table
    print_hour_angle_table(
            latitude=getattr(latitude, angle_output_units),
            rounding_places=rounding_places,
            surface_tilt=getattr(surface_tilt, angle_output_units),
            declination=getattr(solar_declination, angle_output_units),
            hour_angle=getattr(hour_angle, angle_output_units),
            units=angle_output_units,
    )
