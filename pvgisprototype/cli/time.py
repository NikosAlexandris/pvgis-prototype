"""
Important sun and solar surface geometry parameters in calculating the amount of solar radiation that reaches a particular location on the Earth's surface
"""

from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.log import logger
from pandas import DatetimeIndex

from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pathlib import Path
from datetime import datetime
from typing import Annotated, List
from zoneinfo import ZoneInfo

import typer
from rich.console import Console

from pvgisprototype.api.position.models import SolarTimeModel, select_models
from pvgisprototype.api.position.solar_time import calculate_solar_time_series
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.typer.location import (
    typer_argument_longitude,
)
from pvgisprototype.cli.typer.timestamps import (
    typer_option_timezone,
)
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.verbosity import typer_option_quiet, typer_option_verbose
from pvgisprototype.constants import (
    ANGLE_OUTPUT_UNITS_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    CSV_PATH_DEFAULT,
    DATA_TYPE_DEFAULT,
    FINGERPRINT_FLAG_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    LOG_LEVEL_DEFAULT,
    QUIET_FLAG_DEFAULT,
    RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.cli.typer.data_processing import (
    typer_option_array_backend,
    typer_option_dtype,
)
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.output import (
    typer_option_angle_output_units,
    typer_option_csv,
    typer_option_fingerprint,
    typer_option_index,
    typer_option_rounding_places,
)
from pvgisprototype.cli.typer.timestamps import (
    typer_argument_timestamps,
    typer_option_end_time,
    typer_option_frequency,
    typer_option_periods,
    typer_option_random_timestamps,
    typer_option_start_time,
    typer_option_timezone,
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
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(
        now_utc_datetimezone()
    ),
    start_time: Annotated[
        datetime | None, typer_option_start_time
    ] = None,  # Used by a callback function
    periods: Annotated[
        int | None, typer_option_periods
    ] = None,  # Used by a callback function
    frequency: Annotated[
        str | None, typer_option_frequency
    ] = None,  # Used by a callback function
    end_time: Annotated[
        datetime | None, typer_option_end_time
    ] = None,  # Used by a callback function
    timezone: Annotated[str | None, typer_option_timezone] = None,
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    solar_time_model: Annotated[
        List[SolarTimeModel], typer_option_solar_time_model
    ] = [SolarTimeModel.milne],
    angle_output_units: Annotated[
        str, typer_option_angle_output_units
    ] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[
        int, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
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
    # Note the input timestamp and timezone
    user_requested_timestamps = timestamps
    user_requested_timezone = timezone  # Set to UTC by the callback functon !
    timezone = utc_zoneinfo = ZoneInfo('UTC')
    logger.info(
            f"Input time zone : {timezone}",
            alt=f"Input time zone : [code]{timezone}[/code]"
            )

    if timestamps.tz is None:
        timestamps = timestamps.tz_localize(utc_zoneinfo)
        logger.info(
            f"Naive input timestamps\n({user_requested_timestamps})\nlocalized to UTC aware for all internal calculations :\n{timestamps}"
        )

    elif timestamps.tz != utc_zoneinfo:
        timestamps = timestamps.tz_convert(utc_zoneinfo)
        logger.info(
            f"Input zone\n{user_requested_timezone}\n& timestamps :\n{user_requested_timestamps}\n\nconverted for all internal calculations to :\n{timestamps}",
            alt=f"Input zone : [code]{user_requested_timezone}[/code]\n& timestamps :\n{user_requested_timestamps}\n\nconverted for all internal calculations to :\n{timestamps}"
        )

    solar_time_models = select_models(
        SolarTimeModel, solar_time_model
    )  # Using a callback fails!

    solar_time_series = calculate_solar_time_series(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_time_models=solar_time_models,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)

    if not quiet:
        from pvgisprototype.cli.print.solar_time import print_solar_time_series_table

        print_solar_time_series_table(
            longitude=longitude,
            timestamps=timestamps,
            timezone=timezone,
            solar_time_series=solar_time_series,
            title="Solar Time Overview",
            rounding_places=rounding_places,
            index=index,
        )
    if csv:
        pass


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
