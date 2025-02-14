from datetime import datetime
from pvgisprototype.api.series.hardcodings import check_mark, exclamation_mark, x_mark
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import typer
from pandas import Timestamp
from pvgisprototype.log import logger
from pvgisprototype.constants import TIMEZONE_UTC


ZONEINFO_UTC = ZoneInfo(TIMEZONE_UTC)


def parse_timezone(
        timezone: str,
        ) -> ZoneInfo | str:
    """
    """
    context_message = f"> Executing parser function : parse_timestamp()"
    # context_message += f'\ni Callback parameter : {typer.CallbackParam}'
    context_message += f'\n  - Parameter input : {type(timezone)} : {timezone}'
    # context_message += f'\ni Context : {ctx.params}'

    context_message_alternative = f"[yellow]>[/yellow] Executing [underline]parser function[/underline] : parse_timezone()"
    # context_message_alternative += f'\n[yellow]i[/yellow] Callback parameter : {typer.CallbackParam}'
    context_message_alternative += f'\n  - Parameter input : {type(timezone)} : {timezone}'
    # context_message_alternative += f'\n[yellow]i[/yellow] Context: {ctx.params}'

    if not timezone:
        timezone = str()

    elif timezone != 'local':
        timezone = ZoneInfo(timezone)

    context_message += f"\n  < Returning object : {type(timezone)} : {timezone}"
    context_message_alternative += f"\n  [green]<[/green] Returning object : {type(timezone)} : {timezone}"
    logger.info(
            context_message,
            alt=context_message_alternative
            )

    return timezone


def generate_a_timezone(timezone: ZoneInfo) -> ZoneInfo:
    """
    """
    context_message = f"> Executing callback function callback_generate_a_timezone()"
    context_message_alternative = f"[yellow]>[/yellow] Executing [underline]callback function[/underline] callback_generate_a_timezone()"
    logger.info(
            context_message,
            alt=context_message_alternative
            )

    warning_message = warning_message_alternative = str()
    if not timezone:
        warning_message += f"No timezone requested. Assuming and setting {ZONEINFO_UTC}."
        warning_message_alternative += f"[red]No timezone requested.[/red] [bold yellow]Assuming and setting [code]{ZONEINFO_UTC}[/code]."
        logger.warning(
                warning_message,
                alt=warning_message_alternative
                )
        timezone = ZONEINFO_UTC

    if timezone == "local":
        warning_message += f"Local timezone is requested. Retrieving it from the current system."
        warning_message_alternative += f"[bold]Local timezone[/bold] is requested. [bold yellow]Retrieving it from the current system.[/bold yellow]"
        logger.warning(
                warning_message,
                alt=warning_message_alternative
                )
        try:
            timezone = ZoneInfo(Timestamp(datetime.now().astimezone()).tzinfo)

        except (ZoneInfoNotFoundError, Exception):
            logger.error(
                f"{x_mark} Requested zone {timezone} not found. Setting it to UTC.",
                alt=f"[x_mark][red]Requested zone {timezone} not found. Setting it to [code]UTC[/code][/red]."
            )
            raise ValueError('The requested time zone {timezone} is not valid!')

        
    context_message = f"  < Returning object : {type(timezone)} : {timezone}"
    context_message_alternative = f"  [green]<[/green] Returning object : {type(timezone)} : {timezone}"
    logger.info(
            context_message,
            alt=context_message_alternative
            )

    return timezone


def attach_timezone(
    timestamp: Timestamp | None = None,
    timezone: str | None = None
) -> datetime | None:
    """Convert datetime object to timezone-aware."""
    if timestamp is None:
        timestamp = Timestamp.now(tz=ZoneInfo("UTC"))  # Default

    if isinstance(timezone, str):
        try:
            tzinfo = generate_a_timezone(ZoneInfo(timezone))
            timestamp = timestamp.replace(tzinfo=tzinfo)
        except Exception as e:
            raise ValueError(f"Could not convert timezone: {e}")

    return timestamp


def attach_requested_timezone(
    timestamp: Timestamp,
    timezone: ZoneInfo,
) -> Timestamp | None:
    """
    Attaches the requested timezone to a naive datetime. Attention : Defaults to UTC if no timezone requested!
    """
    # print(f'[green]i[/green] Callback function attach_requested_timezone()')

    if timestamp.tzinfo is not None:
        raise ValueError(
            f"  [yellow]>[/yellow] The provided timestamp '{timestamp}' already has a timezone!  Expected a [yellow]naive[/yellow] [bold]datetime[/bold] or [bold]Timestamp[/bold] object."
        )

    if timezone:
        try:
            # print(f'[yellow]i[/yellow] Attaching the requested zone [bold]{timezone}[/bold] to {timestamp}')
            return timestamp.tz_localize(timezone)
        except Exception as e:
            print(
                f"[red]x[/red] Failed to attach the requested timezone '{timezone}' to the timestamp: {e}!"
            )
    else:
        zoneinfo_utc = ZoneInfo("UTC")
        print(
            f"  [yellow]i[/yellow] Timezone not requested! Setting to [red]{zoneinfo_utc}[/red]."
        )
        return timestamp.tz_localize(zoneinfo_utc)


def ctx_attach_requested_timezone(
    ctx: typer.Context,
    timestamp: Timestamp,
    # param: typer.CallbackParam,
) -> Timestamp | None:
    """Returns the current datetime in the user-requested timezone."""

    # print(f'[yellow]i[/yellow] Context: {ctx.params}')
    # print(f'[yellow]i[/yellow] typer.CallbackParam: {param}')
    # print(f'  [yellow]>[/yellow] Executing ctx_attach_requested_timezone()')
    timezone = ctx.params.get("timezone")
    # print(f'  [yellow]>[/yellow] User requested input parameter [code]timezone[/code] = [bold]{timezone}[/bold]')
    # print(f'  [green]>[/green] Callback function returns : {attach_requested_timezone(timestamp, timezone)}')

    return attach_requested_timezone(timestamp, ZoneInfo(timezone))


def callback_generate_a_timezone(
    timezone: str
) -> ZoneInfo:
    """Convert string to `tzinfo` timezone object"""
    return generate_a_timezone(timezone)
