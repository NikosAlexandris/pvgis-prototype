"""
Timestamps

Parameters that relate to the question "When ?".
"""

from pathlib import Path
from zoneinfo import ZoneInfo

import typer
from pandas import DatetimeIndex, Timestamp, Timedelta

from pvgisprototype.api.datetime.datetimeindex import (
    generate_datetime_series,
    generate_timestamps,
)
from pvgisprototype.api.datetime.now import now_local_datetimezone
from pvgisprototype.api.datetime.timezone import (
    callback_generate_a_timezone,
    callback_generate_a_timezone,
    parse_timezone,
)
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_time_series
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT, NEIGHBOR_LOOKUP_DEFAULT, TIMESTAMPS_FREQUENCY_DEFAULT, VERBOSE_LEVEL_DEFAULT
from pvgisprototype.log import logger

timestamp_typer_help = "Quoted date-time string of data to extract from series, example: [yellow]'2112-12-21 21:12:12'[/yellow]'"
timestamps_typer_help = "Quoted date-time strings of data to extract from series, example: [yellow]'2112-12-21, 2112-12-21 12:21:21, 2112-12-21 21:12:12'[/yellow]'"


def print_context(
    ctx: typer.Context,
        ) -> None:
    """
    """
    context = f"Sub/Command name : {ctx.command.name}"
    # context += f"\ninfo_name : {ctx.info_name}"
    context += f"\nPath to sub/command : {ctx.command_path}"
    context += f"\nparent : {ctx.parent}"
    # context += f"\ninvoked_subcommand : {ctx.invoked_subcommand}"
    # context += f"\nget_parameter_source() : {ctx.get_parameter_source('temperature_series')}"
    # context += f"\nget_usage() : {ctx.get_usage()}"
    # context += f"\nmeta : {ctx.meta}"
    # context += f"\nobj : {ctx.obj}"
    # context += f"\nparams : {ctx.params}"

    # print(context)
    logger.info(context)


def parse_timestamp(
    timestamp: str,
    ) -> Timestamp | None:
    """Parse a string meant to be a single datetime stamp and convert it to a
    Pandas Timestamp [1]_.
    """
    if not timestamp:
        return None  # Review me and make me work with NaTType !

    else:
        context_message = f"> Executing parser function : parse_timestamp()"
        # context_message += f'\ni Callback parameter : {typer.CallbackParam}'
        context_message += f'\n  - Parameter input : {type(timestamp)} : {timestamp}'
        # context_message += f'\ni Context : {ctx.params}'

        context_message_alternative = f"[yellow]>[/yellow] Executing [underline]parser function[/underline] : parse_timestamp()"
        # context_message_alternative += f'\n[yellow]i[/yellow] Callback parameter : {typer.CallbackParam}'
        context_message_alternative += f'\n  - Parameter input : {type(timestamp)} : {timestamp}'
        # context_message_alternative += f'\n  [yellow]i[/yellow] Context: {ctx.params}'

        timestamp = Timestamp(timestamp)
        context_message += f"\n  < Returning object : {type(timestamp)} : {timestamp}"
        context_message_alternative += f"\n  < Returning object : {type(timestamp)} : {timestamp}"
        
        logger.info(
                context_message,
                alt=context_message_alternative
                )

        return timestamp


def callback_generate_a_datetime(
    ctx: typer.Context,
    timestamp: Timestamp | None,
) -> Timestamp | None:
    """ """
    if not timestamp:
        return None  # Review me and make me work with NaTType !

    else:
        # print_context(ctx)

        context_message = f"> Executing callback function : callback_generate_a_datetime()"
        # context_message += f'\ni Callback parameter : {typer.CallbackParam}'
        context_message += f'\n  - Parameter input : {type(timestamp)} : {timestamp}'
        # context_message += f'\n  i Context : {ctx.params}'

        context_message_alternative = f"[yellow]>[/yellow] Executing [underline]callback function[/underline] : callback_generate_a_datetime()"
        # context_message_alternative += f'\n[yellow]i[/yellow] Callback parameter : {typer.CallbackParam}'
        context_message_alternative += f'\n  - Parameter input : {type(timestamp)} : {timestamp}'
        context_message_alternative += f'\n  [yellow]i[/yellow] [bold]Context[/bold] : {ctx.params}'
        
        logger.info(
                context_message,
                alt=context_message_alternative
                )

        timezone = ctx.params.get("timezone")
        if timezone:
            logger.info(
                f"  ~ Converting timezone-aware Pandas Timestamp {timestamp} to UTC",
                alt=f"  [bold]~[/bold] Converting timezone-aware Pandas Timestamp {timestamp} to UTC",
            )
            timestamp = Timestamp(timestamp, tz=timezone).tz_convert(ZoneInfo("UTC")).tz_localize(None)
        else:
            timestamp = Timestamp(timestamp)

        logger.info(
                f"  < Returning nonetheless a naive timestamp : {type(timestamp)} : {timestamp}",
                alt=f"  < Returning nonetheless a [bold]naive[/bold] timestamp : {type(timestamp)} : {timestamp}"
        )
        return timestamp


def parse_timestamp_series(
    timestamps: str,
) -> "DatetimeIndex | Timestamp | None":
    """
    Parse an input of type string and generate a Pandas Timestamp or
    DatetimeIndex [1]_.

    either `str`ings or `datetime.datetime` objects and generate a NumPy
    datetime64 array [1]_

    Parameters
    ----------
    timestamps : `str`
            A single `str`ing (i.e. '2111-11-11' or '2121-12-12 12:12:12')

    Returns
    -------
    timestamps :
        Pandas Timestamp or DatetimeIndex

    Notes
    -----
    .. [1] https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Timestamp.html#pandas-timestamp
    .. [2] https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html
    """
    from pandas import to_datetime

    if isinstance(timestamps, str):
        # return to_datetime(timestamps.split(','), format='mixed', utc=True)
        return to_datetime(timestamps.split(","), format="mixed")
    else:
        raise ValueError(
            "The `timestamps` input must be a string of datetime or datetimes separated by comma as expected by Pandas `to_datetime()` function"
        )


def callback_generate_datetime_series(
    ctx: typer.Context,
    timestamps: DatetimeIndex,
):
    """
    Notes
    -----

    On the time offset : 

        - Timestaps of time series data may be or not "full hours".
        - Examples : 
            - ERA5 data are modelled at "full hours"
            - SARAHx climate data records are _not_.
        - Solar positioning, however, needs to coincide with the solar
          irradiance data.

        Solutions :

        1. The solution implemented here (at the moment) is to read the
          official SARAHx auxiliary file with the "true" data acquisition
          timestamps for each location and apply it accordingly at the time of
          generating the timestamps for the calculations.

        2. Alternatively, the SARAHx archive can be re-interpolated in-time
          based on the "SARAH SI[S|D] / TOA" method.  This works due to the
          assumption that the ratio HIR / ToA Irradiance is relatively easier
          to interpolate linearly.

        3. Generate solar positions for the SARA timestamps and ignore the "time
          shift" in ERA5 data.  This introduces "less" errors overall.

        4. In addition to 3. : Interpolate ERAx data at SARAHx data acquisition timestamps.

        5. Ignore the SARAHx "time shift" altogether !

    """
    # print_context(ctx)

    context_message = f"> Executing callback function : callback_generate_datetime_series()"
    # context_message += f'\ni Callback parameter : {typer.CallbackParam}'
    context_message += f'\n  - Parameter input : {type(timestamps)}\n{timestamps}'
    # context_message += f'\n  i Context : {ctx.params}'

    context_message_alternative = f"[yellow]>[/yellow] Executing [underline]callback function[/underline] : callback_generate_datetime_series()"
    # context_message_alternative += f'\n[yellow]i[/yellow] Callback parameter : {typer.CallbackParam}'
    context_message_alternative += f'\n  - Parameter input : {type(timestamps)}\n{timestamps}'
    context_message_alternative += f'\n  [yellow]i[/yellow] Context : {ctx.params}'
    
    logger.info(
            context_message,
            alt=context_message_alternative
            )

    start_time = ctx.params.get("start_time")
    end_time = ctx.params.get("end_time")
    if start_time == end_time:
        logger.warning(
            f"The start {start_time} and end time {end_time} are the same and will generate a single time stamp!",
            alt=f"[yellow bold]The start {start_time} and end time {end_time} are the same and will generate a single time stamp![/yellow bold]",
        )
    periods = ctx.params.get("periods", None)
    frequency = (
        ctx.params.get("frequency", TIMESTAMPS_FREQUENCY_DEFAULT)
        if not periods
        else None
    )

    # Input space-time data files ?
    # global_horizontal_irradiance = ctx.params.get("global_horizontal_irradiance")
    # shortwave = ctx.params.get("shortwave")
    # direct_horizontal_irradiance = ctx.params.get("direct_horizontal_irradiance")
    # direct = ctx.params.get("direct")
    # spectral_factor_series = ctx.params.get("spectral_factor_series")
    # time_series = ctx.params.get("time_series")
    # irradiance = ctx.params.get("irradiance")

    data_file = None
    if any(
        [
            # global_horizontal_irradiance,
            # shortwave,
            # direct_horizontal_irradiance,
            # direct,
            # spectral_factor_series,
            # time_series,
            # irradiance,  # used in the spectral mismatch factor
            ctx.params.get("global_horizontal_irradiance"),
            ctx.params.get("shortwave"),
            ctx.params.get("direct_horizontal_irradiance"),
            ctx.params.get("direct"),
            ctx.params.get("spectral_factor_series"),
            ctx.params.get("time_series"),
            ctx.params.get("irradiance"),
        ]
    ):
        data_file = next(
            filter(
                None,
                [
                    # global_horizontal_irradiance,
                    # direct_horizontal_irradiance,
                    # spectral_factor_series,
                    # time_series,
                    # irradiance,
                    ctx.params.get("global_horizontal_irradiance"),
                    ctx.params.get("shortwave"),
                    ctx.params.get("direct_horizontal_irradiance"),
                    ctx.params.get("direct"),
                    ctx.params.get("spectral_factor_series"),
                    ctx.params.get("time_series"),
                    ctx.params.get("irradiance"),
                ],
            )
        )

    # else:
    #     from pathlib import Path
    #     data_file = None
    if (
        start_time is not None
        or end_time is not None
        or periods is not None
    ):
        start_time = Timestamp(start_time)
        end_time = Timestamp(end_time)
        time_offset = ctx.params.get("time_offset_data")

        timestamps = generate_timestamps(
            data_file=data_file,
            time_offset=time_offset,
            start_time=start_time,
            end_time=end_time,
            periods=periods,
            frequency=frequency,
            timezone=ctx.params.get("timezone"),
            name=ctx.params.get("datetimeindex_name", None),
        )

    logger.info(
            f"The callback function callback_generate_datetime_series() returns the DatetimeIndex : \n{timestamps}",
            alt=f"[bold]The callback function callback_generate_datetime_series() returns the [yellow]DatetimeIndex[/yellow][/bold]: \n{timestamps}"
            )

    return timestamps


def callback_generate_naive_datetime_series(
    ctx: typer.Context,
    timestamps: str,
):
    start_time = ctx.params.get("start_time")
    end_time = ctx.params.get("end_time")
    periods = ctx.params.get("periods", None)
    frequency = (
        ctx.params.get("frequency", TIMESTAMPS_FREQUENCY_DEFAULT)
        if not periods
        else None
    )
    if start_time is not None and end_time is not None:
        timestamps = generate_datetime_series(
            start_time=start_time,
            end_time=end_time,
            periods=periods,
            frequency=frequency,
            timezone=None,
            name=ctx.params.get("datetimeindex_name", None),
        )
    return timestamps


def parse_time_offset_data(
        time_offset_data: str | Path | None,
        )-> Path | None:
    """
    """
    if isinstance(time_offset_data, (str, Path)):
        path = Path(time_offset_data)
        if path.exists():
            return path


from numpy import timedelta64

def callback_generate_time_offset(
    ctx: typer.Context,
    time_offset_data: Timedelta | None,
) -> Timedelta:
    """ """
    from pvgisprototype.api.series.open import read_data_array_or_set

    if isinstance(time_offset_data, Path):

        time_offset_variable = ctx.params.get("time_offset_variable")

        longitude = ctx.params.get("longitude")
        latitude = ctx.params.get("latitude")
        neighbor_lookup = ctx.params.get("neighbor_lookup", NEIGHBOR_LOOKUP_DEFAULT)
        mask_and_scale = ctx.params.get(
            "mask_and_scale", MASK_AND_SCALE_FLAG_DEFAULT
        )
        verbose = ctx.params.get("verbose", VERBOSE_LEVEL_DEFAULT)

        from rich import print
        print(f"{neighbor_lookup=}")

        time_offset_array = read_data_array_or_set(
                input_data=time_offset_data,
                mask_and_scale=mask_and_scale,
                verbose=verbose)[time_offset_variable]

        offset = time_offset_array.sel(
            lon=longitude, lat=latitude, method=neighbor_lookup,
        ).values
        print(f"{offset=}")

        return offset

    return None


typer_option_timezone = typer.Option(
    '--timezone',
    '--tz',
    '--zone',
    help="Timezone (e.g., 'Europe/Athens'). Use the system's time zone via the `--local` option.",
    rich_help_panel=rich_help_panel_time_series,
    is_eager=True,
    parser=parse_timezone,
    callback=callback_generate_a_timezone,
)

warning_overrides_timestamps = "[yellow]Overrides the `timestamps` parameter![/yellow]"
typer_option_start_time = typer.Option(
    '--start-time',
    '--st',
    help=f"Start timestamp of the period. {warning_overrides_timestamps}",
    rich_help_panel=rich_help_panel_time_series,
    # is_eager=True,
    parser=parse_timestamp,
    callback=callback_generate_a_datetime,
)
typer_option_periods = typer.Option(
    help="Number of timestamps to generate",
    rich_help_panel=rich_help_panel_time_series,
    # is_eager=True,
)
typer_option_frequency = typer.Option(
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases
    help="A common date/time frequency unit optionally with a multiples number, such as [code]H[/code](hourly), [code]min[/code](utely), [code]S[/code](econdly), [code]D[/code](aily), [code]W[/code](eekly), [code]M[/code](onth end), [code]Y[/code](early) or [code]30min[/code]. See Pandas time series offset aliases.",
    rich_help_panel=rich_help_panel_time_series,
    # is_eager=True,
)
typer_option_end_time = typer.Option(
    '--end-time',
    '--et',
    help=f"End timestamp of the period. {warning_overrides_timestamps}",
    rich_help_panel=rich_help_panel_time_series,
    # is_eager=True,
    parser=parse_timestamp,
    callback=callback_generate_a_datetime,
)
typer_option_local_time = typer.Option(
    help="Use the system's local time zone",
    rich_help_panel=rich_help_panel_time_series,
    callback=now_local_datetimezone,
)
typer_argument_timestamps = typer.Argument(
    help=timestamps_typer_help,
    rich_help_panel=rich_help_panel_time_series,
    # is_eager=True,
    parser=parse_timestamp_series,
    callback=callback_generate_datetime_series,
    # default_factory=now_utc_datetimezone,
    show_default=False,
)
typer_argument_naive_timestamps = typer.Argument(
    help=timestamps_typer_help,
    rich_help_panel=rich_help_panel_time_series,
    # is_eager=True,
    parser=parse_timestamp_series,
    callback=callback_generate_naive_datetime_series,
    # default_factory=now_utc_datetimezone,
    show_default=False,
)
typer_option_timestamps = typer.Option(
    help="Timestamps",
    rich_help_panel=rich_help_panel_time_series,
    # is_eager=True,
    parser=parse_timestamp_series,
    callback=callback_generate_datetime_series,
    #     default_factory=now_utc_datetimezone_series,
)
typer_option_time_offset_data = typer.Option(
    help="Time offset to add to timestamps",
    rich_help_panel=rich_help_panel_time_series,
    # is_eager=True,
    parser=parse_time_offset_data,
    callback=callback_generate_time_offset,
)
typer_option_time_offset_variable = typer.Option(
    help="Variable name of the time offset (difference) data",
    rich_help_panel=rich_help_panel_time_series,
    is_eager=True,
)

typer_option_random_day = typer.Option(
    help="Generate a random day to demonstrate calculation",
    rich_help_panel=rich_help_panel_time_series,
)
typer_option_random_days = typer.Option(
    help="Generate random days to demonstrate calculation",
    rich_help_panel=rich_help_panel_time_series,
)
typer_option_random_time = typer.Option(
    help="Generate a random date, time and timezone to demonstrate calculation",
    rich_help_panel=rich_help_panel_time_series,
)
typer_option_random_timestamps = typer.Option(
    help="Generate a random date, time and timezone to demonstrate calculation",
    rich_help_panel=rich_help_panel_time_series,
    # show_default=False,
    show_choices=False,
)
