from datetime import datetime
from typing import Union
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import typer
from pandas import Timestamp


def convert_to_timezone(timezone: str) -> ZoneInfo:
    """Convert string to ZoneInfo object."""
    # print(f'[yellow]i[/yellow] Executing convert_to_timezone()')

    if timezone is None:
        # print(f'  [yellow]>[/yellow] No timezone requested [red]?[/red]')  # Convert to warning!
        # print(f'  [yellow]>[/yellow] Setting timezone to [red]UTC[/red]')
        return ZoneInfo("UTC")

    else:
        try:
            if timezone == "local":
                return datetime.now().astimezone(None).tzinfo

            else:
                return ZoneInfo(timezone)

        except (ZoneInfoNotFoundError, Exception):
            print(
                f"  [yellow]>[/yellow] Requested zone {timezone} not found. Setting it to [red]UTC[/red]."
            )
            return ZoneInfo("UTC")


def attach_timezone(
    timestamp: datetime | None = None, timezone: str | None = None
) -> datetime | None:
    """Convert datetime object to timezone-aware."""
    if timestamp is None:
        timestamp = datetime.now(ZoneInfo("UTC"))  # Default to UTC

    if isinstance(timezone, str):
        try:
            tzinfo = convert_to_timezone(timezone)
            timestamp = timestamp.replace(tzinfo=tzinfo)
        except Exception as e:
            raise ValueError(f"Could not convert timezone: {e}")

    return timestamp


def attach_requested_timezone(
    timestamp: Union[Timestamp, datetime],
    timezone: ZoneInfo = None,
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
    ctx: typer.Context, timestamp: str, param: typer.CallbackParam
) -> datetime:
    """Returns the current datetime in the user-requested timezone."""

    # print(f'[yellow]i[/yellow] Context: {ctx.params}')
    # print(f'[yellow]i[/yellow] typer.CallbackParam: {param}')
    # print(f'  [yellow]>[/yellow] Executing ctx_attach_requested_timezone()')
    timezone = ctx.params.get("timezone")
    # print(f'  [yellow]>[/yellow] User requested input parameter [code]timezone[/code] = [bold]{timezone}[/bold]')
    # print(f'  [green]>[/green] Callback function returns : {attach_requested_timezone(timestamp, timezone)}')

    from pandas import to_datetime

    return attach_requested_timezone(to_datetime(timestamp), timezone)


def ctx_convert_to_timezone(ctx: typer.Context, param: typer.CallbackParam, value: str):
    """Convert string to `tzinfo` timezone object"""
    return convert_to_timezone(value)
