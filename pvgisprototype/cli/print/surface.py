#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from zoneinfo import ZoneInfo
from pandas import DatetimeIndex
from rich.box import SIMPLE_HEAD
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from scipy.optimize import OptimizeResult, minimize

from pvgisprototype.cli.print.helpers import infer_frequency_from_timestamps
from pvgisprototype.cli.print.caption import build_simple_caption
from pvgisprototype.cli.print.fingerprint import retrieve_fingerprint
from pvgisprototype.cli.print.legend import build_legend_table
from pvgisprototype.cli.print.time import build_time_table, build_time_panel
from pvgisprototype.cli.print.panels import build_version_and_fingerprint_columns
from pvgisprototype.cli.surface.optimiser import optimal_surface_position
from pvgisprototype.constants import (
    ANGLE_UNIT_NAME,
    INCIDENCE_DEFINITION,
    LATITUDE_COLUMN_NAME,
    LONGITUDE_COLUMN_NAME,
    ROUNDING_PLACES_DEFAULT,
    SURFACE_ORIENTATION_NAME,
    SURFACE_TILT_NAME,
    UNIT_NAME,
)
from rich.columns import Columns
from rich.box import HORIZONTALS, ROUNDED
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype import OptimalSurfacePosition

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
    table = Table(
        box=None,
        show_header=False,
        show_edge=False,
        pad_edge=False,
    )
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


def build_surface_position_table(
    title: str | None = "Surface Position",
    # index: bool,
    # surface_position_data,
    # timestamps,
    # rounding_places,
    # keys_to_sum: dict,
    # keys_to_average: dict,
    # keys_to_exclude: dict,
    # time_column_name: RenderableType = "Time",
    # time_column_footer: RenderableType = SYMBOL_SUMMATION,
    # time_column_footer_style: str = "purple",
):
    """
    """
    table = Table(
        title=title,
        title_style='dim',
        # caption=caption.rstrip(', '),  # Remove trailing comma + space
        # caption_justify="left",
        # expand=False,
        # padding=(0, 1),
        # box=SIMPLE_HEAD,
        box=None,
        show_edge=False,
        pad_edge=False,
        # header_style="bold gray50",
        show_header=True,
        header_style=None,
        # show_footer=True,
        # footer_style='white',
        row_styles=["none", "dim"],
        highlight=True,
    )
    table.add_column(
        "Parameter",
        justify="right",
        style="dim",
        no_wrap=True,
    )
    table.add_column(
        "Angle",
        justify="right",
    )
    table.add_column(
        "Unit",
        # justify="left",
    )
    table.add_column(
        "Optimised",
        style="bold",
        justify="center",
    )
    table.add_column(
        "Range",
        justify="left",
        style="dim",
    )

    return table


def print_optimal_surface_position_output(
    surface_position_data: dict,
    surface_position: OptimalSurfacePosition,
    surface_orientation: bool = True,
    min_surface_orientation: float | None = None,
    max_surface_orientation: float | None = None,
    surface_tilt: bool = True,
    min_surface_tilt: float | None = None,
    max_surface_tilt: float | None = None,
    photovoltaic_power: bool = True,
    timestamps: DatetimeIndex | None = None,
    timezone: ZoneInfo = ZoneInfo('UTC'),
    title: str | None = None,  #"Optimal Position",
    title_power: str | None = None,
    subtitle_power: str | None = "Photovoltaic Power",
    subtitle_position: str | None = "Surface Position",
    subtitle_metadata = "Metadata",
    version: bool = False,
    fingerprint: bool = False,
    rounding_places: int = 3,
) -> None:
    """
    Print surface optimisation results in a clean, minimal panel format.
    
    Parameters
    ----------
    result : dict
        Dictionary containing optimisation results with keys:
        - 'Surface Orientation': dict with 'value', 'optimal', 'unit'
        - 'Surface Tilt': dict with 'value', 'optimal', 'unit'
        - 'Mean PV Power': float
        - 'Unit': str (angle unit)
        - 'Timing': str (algorithm name)
        - 'Fingerprint 🆔': str (optional)
    rounding_places : int, default=3
        Number of decimal places for rounding
    """
    # from devtools import debug
    # debug(surface_position)

    # Time might be Local 

    # if user_requested_timestamps is not None:
    #     time_column_name = LOCAL_TIME_COLUMN_NAME
    # else:
    #     time_column_name = TIME_COLUMN_NAME

    # if timestamps is not None:
    #     if user_requested_timezone is not None:
    #         if user_requested_timezone != ZoneInfo("UTC"):
    #             time_column_name = LOCAL_TIME_COLUMN_NAME
    #             timezone_string = f"Local Zone: [bold]{timezone}[/bold]"
    #         else:
    #             time_column_name = TIME_COLUMN_NAME

    if timezone:
        if timezone == ZoneInfo('UTC'):
            timezone_string = f"[bold]{timezone}[/bold]"
        else:
            timezone_string = f"Local Zone: [bold]{timezone}[/bold]"

    # Collect output data
    
    if surface_orientation:
        # orientation = surface_position_data.get('Surface Orientation', {})
        orientation = surface_position.surface_orientation
        orientation.value = round_float_values(orientation.value, rounding_places)
        orientation.optimal = "[green]✓[/green]" if orientation.optimal else "[red]✗[/red]"
        if min_surface_orientation and max_surface_orientation:
            orientation_range = f"[{min_surface_orientation}, {max_surface_orientation}]"

    if surface_tilt:
        tilt = surface_position.surface_tilt
        tilt.value = round_float_values(tilt.value, rounding_places)
        tilt.optimal = "[green]✓" if tilt.optimal else "[red]✗"
        tilt_range = f"[{min_surface_tilt}, {max_surface_tilt}]"

    if photovoltaic_power:
        minimum_power = float()
        mean_power = surface_position.mean_photovoltaic_power
        maximum_power = float()

        if mean_power is not None:
            mean_power = round_float_values(float(mean_power), rounding_places)

    # Build output table

    photovoltaic_power_table = Table(
        title=title_power,
        title_style='dim',
        # caption=caption.rstrip(', '),  # Remove trailing comma + space
        # caption_justify="left",
        # expand=False,
        # padding=(0, 1),
        # box=SIMPLE_HEAD,
        box=None,
        show_edge=False,
        pad_edge=False,
        # header_style="bold gray50",
        show_header=True,
        header_style=None,
        # show_footer=True,
        # footer_style='white',
        row_styles=["none", "dim"],
        highlight=True,
    )
    photovoltaic_power_table.add_column(
        "Statistic",
        justify="right",
        style="dim",
        no_wrap=True,
    )
    photovoltaic_power_table.add_column(
        "Power",
        justify="right",
    )
    photovoltaic_power_table.add_column(
        "Unit",
        # justify="left",
    )

    surface_position_table = build_surface_position_table(title=title)

    # Populate output table

    minimum_photovoltaic_power_row = []
    photovoltaic_power_row = []
    maximum_photovoltaic_power_row = []

    orientation_row = []
    tilt_row = []

    if surface_orientation:
        # surface_orientation_output = "Surface Orientation ⯐ "
        orientation_row.append("Orientation ⯐")
        orientation_row.append(f"{orientation.value}")
        orientation_row.append(f"{orientation.unit}")
        orientation_row.append(f"{orientation.optimal}")

        if min_surface_orientation and max_surface_orientation:
            orientation_row.append(orientation_range)

        surface_position_table.add_row(*orientation_row)

    if surface_tilt:
        tilt_row.append("Tilt ⯐")
        tilt_row.append(f"{tilt.value}")
        tilt_row.append(f"{tilt.unit}")
        tilt_row.append(f"{tilt.optimal}")

        if tilt_range:
            tilt_row.append(tilt_range)

        surface_position_table.add_row(*tilt_row)

    if photovoltaic_power:
        minimum_photovoltaic_power_row.append("Min")
        minimum_photovoltaic_power_row.append(f"[dim]{minimum_power}[/dim]")
        minimum_photovoltaic_power_row.append('W')
        photovoltaic_power_table.add_row(*minimum_photovoltaic_power_row)

        photovoltaic_power_row.append("Mean")
        photovoltaic_power_row.append(f"[bold yellow]{mean_power}[/bold yellow]")
        photovoltaic_power_row.append('W')
        photovoltaic_power_table.add_row(*photovoltaic_power_row)

        maximum_photovoltaic_power_row.append("Max")
        maximum_photovoltaic_power_row.append(f"[dim]{maximum_power}[/dim]")
        maximum_photovoltaic_power_row.append('W')
        photovoltaic_power_table.add_row(*maximum_photovoltaic_power_row)

    # Metadata

    metadata_table = Table(
        box=None,
        show_header=False,
        show_edge=False,
        pad_edge=False,
    )
    metadata_table.add_column(
        justify="right",
        style="none",
        no_wrap=True,
    )
    metadata_table.add_column(justify="left")

    # Build Panels

    time_table = build_time_table()
    frequency, frequency_label = infer_frequency_from_timestamps(timestamps)
    time_table.add_row(
        str(timestamps.strftime("%Y-%m-%d %H:%M").values[0]),
        str(frequency) if frequency and frequency != "Single" else "-",
        str(timestamps.strftime("%Y-%m-%d %H:%M").values[-1]),
        str(timezone_string),
    )
    time_panel = build_time_panel(time_table, padding=(0, 1, 2, 1))

    power_panel = Panel(
        photovoltaic_power_table,
        # title="Optimisation Results",
        subtitle=subtitle_power,
        subtitle_align='right',
        # box=HORIZONTALS,
        # box=SIMPLE_HEAD,
        safe_box=True,
        style="",
        border_style='dim',
        expand=False,
        padding=(0, 1),
    )

    position_panel = Panel(
        surface_position_table,
        # title="Optimisation Results",
        subtitle=subtitle_position,
        subtitle_align='right',
        # box=HORIZONTALS,
        # box=SIMPLE_HEAD,
        safe_box=True,
        style="",
        border_style='dim',
        expand=False,
        padding=(0, 1, 1, 1),
    )

    # Metadata Panel

    # Timing algorithm

    timing = surface_position_data.get("Timing")
    if timing:
        metadata_table.add_row("Timing :", f"[bold]{timing}[/bold]")

    # Version & Fingerprint

    fingerprint = retrieve_fingerprint(dictionary=surface_position_data)
    version_and_fingerprint_and_column = build_version_and_fingerprint_columns(
        version=version,
        fingerprint=fingerprint,
    )

    metadata_panel = Panel(
        metadata_table,
        subtitle=f"[dim]{subtitle_metadata}[/dim]",
        box=ROUNDED,
        style="dim",
        border_style="dim",
        expand=False,
        padding=(0, 1),
    )

    panels = []
    panels.append(power_panel)
    panels.append(position_panel)
    panels.append(time_panel)
    panels.append(metadata_panel)

    # Print columns

    columns = Columns(
        panels,
        # expand=False,
        # equal=True,
        # padding=2,
    )
    console.print(columns)
