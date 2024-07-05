"""
Important sun and solar surface geometry parameters in calculating the amount of solar radiation that reaches a particular location on the Earth's surface
"""

from datetime import datetime
from typing import Annotated, List, Optional
from zoneinfo import ZoneInfo

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from pvgisprototype.api.position.models import SolarTimeModel, select_models
from pvgisprototype.api.position.solar_time import calculate_solar_time_series
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.typer.earth_orbit import (
    typer_option_eccentricity_correction_factor,
    typer_option_perigee_offset,
)
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.typer.location import (
    typer_argument_latitude,
    typer_argument_longitude,
)
from pvgisprototype.cli.typer.timestamps import (
    typer_argument_timestamp,
    typer_option_timezone,
)
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.constants import (
    ECCENTRICITY_CORRECTION_FACTOR,
    PERIGEE_OFFSET,
    SOLAR_TIME_COLUMN_NAME,
    SOLAR_TIME_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    TIME_ALGORITHM_NAME,
)

app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help="⌛ Calculate the solar time for a location and moment",
)
console = Console()


@app.command(
    "fractional-year",
    no_args_is_help=True,
    help=f"⦩ Calculate the fractional year {NOT_IMPLEMENTED_CLI}",
)
def fractional_year():
    """ """
    pass


@app.command(
    "eot",
    no_args_is_help=True,
    help=f"⦩ Calculate the equation of time {NOT_IMPLEMENTED_CLI}",
)
def equation_of_time():
    """ """
    pass


@app.command(
    "offset",
    no_args_is_help=True,
    help=f"⦩ Calculate the time offset {NOT_IMPLEMENTED_CLI}",
)
def offset():
    """ """
    pass


@app.command("solar", no_args_is_help=True, help="⦩ Calculate the apparent solar time")
def solar_time(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    solar_time_model: Annotated[List[SolarTimeModel], typer_option_solar_time_model] = [
        SolarTimeModel.skyfield
    ],
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[
        float, typer_option_eccentricity_correction_factor
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    verbose: Annotated[int, typer_option_verbose] = 0,
):
    """Calculate the solar time.

    1. Map the day of the year onto the circumference of a circle, essentially
    converting the day of the year into radians.

    2. Approximate empirically the equation of time, which accounts for the
    elliptical shape of Earth's orbit and the tilt of its axis.

    3. Calculate the solar time by adding the current hour of the year, the
    time offset from the equation of time, and the hour offset (likely a
    longitude-based correction).
    """
    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tz != utc_zoneinfo:
        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        timezone = utc_zoneinfo
        typer.echo(
            f"The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!"
        )

    solar_time_model = select_models(
        SolarTimeModel, solar_time_model
    )  # Using a callback fails!
    solar_time_series = calculate_solar_time_series(
        # longitude=longitude,
        # latitude=latitude,
        # timestamp=timestamp,
        # timezone=timezone,
        # solar_time_models=solar_time_model,  # keep the CLI simple
        # perigee_offset=perigee_offset,
        # eccentricity_correction_factor=eccentricity_correction_factor,
        # verbose=verbose,
    )
    solar_time_table = Table(
        TIME_ALGORITHM_COLUMN_NAME,
        SOLAR_TIME_COLUMN_NAME,
        box=box.SIMPLE_HEAD,  # UNIT_NAME,
    )
    for model_result in solar_time_series:
        # typer.echo(f'Solar time: {solar_time} {units} ({timezone})')
        model_name = model_result.get(TIME_ALGORITHM_NAME, "")
        solar_time = model_result.get(SOLAR_TIME_NAME, "")
        # units = model_result.get(UNIT_NAME, '')
        solar_time_table.add_row(
            model_name,
            str(solar_time),
            # str(units),
        )
    console.print(solar_time_table)


@app.command(
    "local",
    no_args_is_help=True,
    help=f"⦩ Calculate the local time {NOT_IMPLEMENTED_CLI}",
)
def local():
    """ """
    pass


@app.command(
    "correction",
    no_args_is_help=True,
    help=f"⦩ Calculate the time correction {NOT_IMPLEMENTED_CLI}",
)
def correction():
    """ """
    pass


if __name__ == "__main__":
    app()
