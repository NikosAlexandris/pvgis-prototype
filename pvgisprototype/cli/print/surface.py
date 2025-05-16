from rich.box import HORIZONTALS
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pvgisprototype.cli.print.caption import build_simple_caption
from pvgisprototype.cli.print.legend import build_legend_table
from pvgisprototype.cli.print.panels import build_version_and_fingerprint_columns
from pvgisprototype.constants import ANGLE_UNIT_NAME, INCIDENCE_DEFINITION, LATITUDE_COLUMN_NAME, LONGITUDE_COLUMN_NAME, ROUNDING_PLACES_DEFAULT, SURFACE_ORIENTATION_NAME, SURFACE_TILT_NAME, UNIT_NAME

console = Console()


def print_surface_position_table(
    surface_position: dict,
    longitude,
    latitude,
    timezone,
    title="Surface Position",
    version: bool = False,
    fingerprint: bool = False,
    rounding_places=ROUNDING_PLACES_DEFAULT,
):
    """
    """
    panels = []
    caption = build_simple_caption(
        longitude,
        latitude,
        surface_position,
        timezone,
        user_requested_timezone=None,
    )
    # then : Create a Legend table for the symbols in question
    legend = build_legend_table(
        dictionary=surface_position,
        caption=caption,
        show_header=False,
        box=None,
    )
    caption_panel = Panel(
        caption,
        subtitle="[gray]Reference[/gray]",
        subtitle_align="right",
        border_style="dim",
        expand=False
    )
    legend_panel = Panel(
        legend,
        subtitle="[dim]Legend[/dim]",
        subtitle_align="right",
        border_style="dim",
        expand=False,
        padding=(0,1),
        # style="dim",
    )
    # surface position Panel
    table = Table(box=None, show_header=False, show_edge=False, pad_edge=False)
    table.add_column(justify="right", style="none", no_wrap=True)
    table.add_column(justify="left")
    table.add_row(f"{LATITUDE_COLUMN_NAME} :", f"[bold]{latitude}[/bold]")
    table.add_row(f"{LONGITUDE_COLUMN_NAME} :", f"[bold]{longitude}[/bold]")
    # table.add_row("Time :", f"{timestamp[0]}")
    table.add_row("Time zone :", f"{timezone}")
    longest_label_length = max(len(key) for key in surface_position.keys())
    surface_position_keys = {
        SURFACE_ORIENTATION_NAME,
        SURFACE_TILT_NAME,
        ANGLE_UNIT_NAME,
        INCIDENCE_DEFINITION,
        UNIT_NAME,
    }
    for key, value in surface_position.items():
        if key in surface_position_keys:
            padded_key = f"{key} :".ljust(longest_label_length + 3, " ")
            if key == INCIDENCE_DEFINITION:
                value = f"[yellow]{value}[/yellow]"
            table.add_row(padded_key, str(value))
    position_panel = Panel(
        table,
        title="Surface Position",
        box=HORIZONTALS,
        style="",
        expand=False,
        padding=(0, 2),
    )
    panels.append(position_panel)
    version_and_fingerprint_and_column = build_version_and_fingerprint_columns(
        version=version,
        fingerprint=fingerprint,
    )
    # Use Columns to place them side-by-side
    from rich.columns import Columns

    console.print(Columns([
            caption_panel,
            legend_panel,
        ]))
    console.print(version_and_fingerprint_and_column)
