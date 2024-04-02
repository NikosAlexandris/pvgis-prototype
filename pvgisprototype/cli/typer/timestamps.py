"""
Timestamps

Parameters that relate to the question "When ?".
"""

import typer
from pvgisprototype.api.utilities.timestamp import ctx_attach_requested_timezone
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import parse_timestamp_series
from pvgisprototype.api.utilities.timestamp import callback_generate_datetime_series
from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.api.utilities.timestamp import now_local_datetimezone
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_time_series


timestamp_typer_help = "Quoted date-time string of data to extract from series, example: [yellow]'2112-12-21 21:12:12'[/yellow]'"
typer_argument_timestamp = typer.Argument(
    help=timestamp_typer_help,
    callback=ctx_attach_requested_timezone,
    # rich_help_panel=rich_help_panel_time_series,
    default_factory=now_utc_datetimezone,
    show_default=False,
)
timestamps_typer_help = "Quoted date-time strings of data to extract from series, example: [yellow]'2112-12-21, 2112-12-21 12:21:21, 2112-12-21 21:12:12'[/yellow]'"
typer_argument_timestamps = typer.Argument(
    help=timestamps_typer_help,
    parser=parse_timestamp_series,
    callback=callback_generate_datetime_series,
#     default_factory=now_utc_datetimezone_series,
    show_default=False,
)
typer_option_timestamps = typer.Option(
    help='Timestamps',
    parser=parse_timestamp_series,
    callback=callback_generate_datetime_series,
#     default_factory=now_utc_datetimezone_series,
)
warning_overrides_timestamps = f'[yellow]Overrides the `timestamps` parameter![/yellow]'
typer_option_start_time = typer.Option(
    help=f'Start timestamp of the period. {warning_overrides_timestamps}',
    rich_help_panel=rich_help_panel_time_series,
    default_factory = None,
)
typer_option_periods = typer.Option(
    help=f"Number of timestamps to generate",
    rich_help_panel=rich_help_panel_time_series,
    # default_factory=None
)
typer_option_frequency = typer.Option(
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases
    help=f"A common date/time frequency unit optionally with a multiples number, such as [code]H[/code](hourly), [code]min[/code](utely), [code]S[/code](econdly), [code]D[/code](aily), [code]W[/code](eekly), [code]M[/code](onth end), [code]Y[/code](early) or [code]30m[/code]. See Pandas time series offset aliases.",
    rich_help_panel=rich_help_panel_time_series,
    # default_factory='h'
)
typer_option_end_time = typer.Option(
    help=f'End timestamp of the period. {warning_overrides_timestamps}',
    rich_help_panel=rich_help_panel_time_series,
    default_factory = None,
)
typer_option_timezone = typer.Option(
    # help='Timezone (e.g., "Europe/Athens"). Set _local_ to use the system\'s time zone',
    help="Timezone (e.g., 'Europe/Athens'). Use the system's time zone via the --local option.",
    callback=ctx_convert_to_timezone,
    # default_factory=None,
)
typer_option_local_time = typer.Option(
    help="Use the system's local time zone",
    callback=now_local_datetimezone
)
typer_option_random_time = typer.Option(
    # '--random-time',
    # '--random',
    help='Generate a random date, time and timezone to demonstrate calculation'
)
typer_option_random_day = typer.Option(
    # '--random-day',
    # '--random',
    help='Generate a random day to demonstrate calculation',
    # default_factory=RANDOM_DAY_FLAG_DEFAULT,
)
typer_option_random_days = typer.Option(
    # '--random-day',
    # '--random',
    help='Generate random days to demonstrate calculation',
    # default_factory=RANDOM_DAY_FLAG_DEFAULT,
)
