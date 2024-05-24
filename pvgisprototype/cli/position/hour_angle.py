from rich import print
from typing import Annotated
from typing import Optional

from pvgisprototype.cli.typer.timing import typer_argument_true_solar_time
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.verbosity import typer_option_verbose

from pvgisprototype.api.position.hour_angle import calculate_solar_hour_angle
from pvgisprototype.cli.print import print_hour_angle_table_2

from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT


def hour_angle(
    solar_time: Annotated[float, typer_argument_true_solar_time],
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

    #
    # Update Me
    #

    hour_angle = calculate_solar_hour_angle(
        solar_time=solar_time,
    )
    print_hour_angle_table_2(
        solar_time=solar_time,
        rounding_places=rounding_places,
        hour_angle=getattr(hour_angle, angle_output_units),
        units=angle_output_units,
    )
    print(f'Hour angle: {getattr(hour_angle, angle_output_units)} {angle_output_units}')
