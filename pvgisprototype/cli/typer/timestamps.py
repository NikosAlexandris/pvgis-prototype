"""
Timestamps

Parameters that relate to the question "When ?".
"""

from datetime import datetime

import typer
from pandas import DatetimeIndex

from pvgisprototype.api.datetime.datetimeindex import (
    generate_datetime_series,
    parse_timestamp_series,
)
from pvgisprototype.api.datetime.now import now_local_datetimezone
from pvgisprototype.api.datetime.timezone import (
    ctx_attach_requested_timezone,
    ctx_convert_to_timezone,
)
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_time_series
from pvgisprototype.constants import TIMESTAMPS_FREQUENCY_DEFAULT
from pvgisprototype.log import logger

timestamp_typer_help = "Quoted date-time string of data to extract from series, example: [yellow]'2112-12-21 21:12:12'[/yellow]'"
timestamps_typer_help = "Quoted date-time strings of data to extract from series, example: [yellow]'2112-12-21, 2112-12-21 12:21:21, 2112-12-21 21:12:12'[/yellow]'"


def callback_generate_datetime_series(
    ctx: typer.Context,
    timestamps: DatetimeIndex,
    # timestamps: List[datetime],
    # value: Union[str, datetime, List[datetime]],
    # param: typer.CallbackParam,
):
    # print(f'[yellow]i[/yellow] Context: {ctx.params}')
    # print(f'[yellow]i[/yellow] typer.CallbackParam: {param}')
    # print("[yellow]i[/yellow] Executing callback_generate_datetime_series()")
    # print(f'  Input [yellow]timestamps[/yellow] : {timestamps}')
    start_time = ctx.params.get("start_time")
    end_time = ctx.params.get("end_time")
    if start_time == end_time:
        logger.warning(
            (
                "[yellow bold]The start and end time are the same and will generate a single time stamp![/yellow bold]"
            )
        )
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
            timezone=ctx.params.get("timezone"),
            name=ctx.params.get("datetimeindex_name", None),
        )
    # from pandas import to_datetime
    # -----------------------------------------------------------------------
    # If we do the following, we need to take care of external naive time series!
    # timezone_aware_timestamps = [
    #     attach_requested_timezone(timestamp, timezone) for timestamp in timestamps
    # ]
    # return to_datetime(timezone_aware_timestamps, format="mixed")
    # -----------------------------------------------------------------------
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


typer_argument_timestamp = typer.Argument(
    help=timestamp_typer_help,
    callback=ctx_attach_requested_timezone,
    # rich_help_panel=rich_help_panel_time_series,
    # default_factory=now_utc_datetimezone,
    show_default=False,
)
typer_argument_timestamps = typer.Argument(
    help=timestamps_typer_help,
    rich_help_panel=rich_help_panel_time_series,
    is_eager=True,
    parser=parse_timestamp_series,
    callback=callback_generate_datetime_series,
    # default_factory=now_utc_datetimezone,
    show_default=False,
)
typer_argument_naive_timestamps = typer.Argument(
    help=timestamps_typer_help,
    rich_help_panel=rich_help_panel_time_series,
    is_eager=True,
    parser=parse_timestamp_series,
    callback=callback_generate_naive_datetime_series,
    # default_factory=now_utc_datetimezone,
    show_default=False,
)
typer_option_timestamps = typer.Option(
    help="Timestamps",
    rich_help_panel=rich_help_panel_time_series,
    is_eager=True,
    parser=parse_timestamp_series,
    callback=callback_generate_datetime_series,
    #     default_factory=now_utc_datetimezone_series,
)


def convert_datetime_to_Timestamp(timestamp: datetime):
    """ """
    from pandas import Timestamp

    if not timestamp:
        return None
    return Timestamp(timestamp)


warning_overrides_timestamps = "[yellow]Overrides the `timestamps` parameter![/yellow]"
typer_option_start_time = typer.Option(
    help=f"Start timestamp of the period. {warning_overrides_timestamps}",
    rich_help_panel=rich_help_panel_time_series,
    is_eager=True,
    callback=convert_datetime_to_Timestamp,
)
typer_option_periods = typer.Option(
    help="Number of timestamps to generate",
    rich_help_panel=rich_help_panel_time_series,
    is_eager=True,
)
typer_option_frequency = typer.Option(
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases
    help="A common date/time frequency unit optionally with a multiples number, such as [code]H[/code](hourly), [code]min[/code](utely), [code]S[/code](econdly), [code]D[/code](aily), [code]W[/code](eekly), [code]M[/code](onth end), [code]Y[/code](early) or [code]30m[/code]. See Pandas time series offset aliases.",
    rich_help_panel=rich_help_panel_time_series,
    is_eager=True,
)
typer_option_end_time = typer.Option(
    help=f"End timestamp of the period. {warning_overrides_timestamps}",
    rich_help_panel=rich_help_panel_time_series,
    is_eager=True,
    callback=convert_datetime_to_Timestamp,
)
typer_option_timezone = typer.Option(
    help="Timezone (e.g., 'Europe/Athens'). Use the system's time zone via the `--local` option.",
    rich_help_panel=rich_help_panel_time_series,
    is_eager=True,
    callback=ctx_convert_to_timezone,
)
typer_option_local_time = typer.Option(
    help="Use the system's local time zone",
    rich_help_panel=rich_help_panel_time_series,
    callback=now_local_datetimezone,
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
)
