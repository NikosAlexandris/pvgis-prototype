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
from pvgisprototype.constants import NOT_AVAILABLE, SYMBOL_SUMMATION
from pvgisprototype.cli.print.getters import (
    get_scalar,
)
from typing import Sequence
from numpy import datetime64
from rich.table import Table
from rich.panel import Panel
from rich.console import Console, RenderableType
from rich.columns import Columns
from rich.text import Text
from rich import print
from pvgisprototype.api.position.models import (
    SolarPositionParameter,
    SolarPositionParameterColumnName,
    SolarEvent,
)
from pvgisprototype.cli.print.irradiance.text import format_string
from pvgisprototype.api.utilities.conversions import round_float_values
from pandas import to_datetime, isna
import numpy


def build_solar_position_table(
    title: str,
    index: bool,
    input_table: dict,
    dictionary: dict,
    position_parameters: Sequence[SolarPositionParameter],
    # timestamps,
    # rounding_places: int,
    time_column_name: str,
    time_column_footer: RenderableType = SYMBOL_SUMMATION,
    time_column_footer_style: str = "purple",
    # keys_to_sum = KEYS_TO_SUM,
    # keys_to_average = KEYS_TO_AVERAGE,
    # keys_to_exclude = KEYS_TO_EXCLUDE,
) -> Table:
    from rich.table import Table
    from rich.box import SIMPLE_HEAD

    table = Table(
        title=title,
        caption_justify="left",
        expand=False,
        padding=(0, 1),
        box=SIMPLE_HEAD,
        show_footer=True,
        show_header=True,
        header_style="bold",  # "bold gray50",
        row_styles=["none", "dim"],
        highlight=True,  # To light or Not ?
    )

    # base columns
    if index:
        table.add_column("Index")

    ## Time column

    table.add_column(
        time_column_name,
        justify="left",
        no_wrap=True,
        footer=time_column_footer,
        footer_style=time_column_footer_style,
    )

    # remove the 'Title' entry! ---------------------------------------------
    dictionary.pop("Title", NOT_AVAILABLE)
    # ------------------------------------------------------------- Important

    first_model = input_table[next(iter(input_table))]

    # Pull out the two relevant nested dicts
    first_model = input_table[next(iter(input_table))]
    core_data = first_model.get("Core", {})
    events_data = first_model.get("Solar Events", {})

    # For each requested parameter, derive its header and find its data
    for parameter in position_parameters:
        # Skip enum members without a matching ColumnName
        if parameter.name not in SolarPositionParameterColumnName.__members__:
            continue

        # Get the human-readable header from the ColumnName enum
        header = SolarPositionParameterColumnName[parameter.name].value

        # Look first in Core, then in Solar Events
        if header in core_data:
            value = core_data[header]
        elif header in events_data:
            value = events_data[header]
        else:
            continue  # not present

        # # skip event columns when array has no real entries
        # if parameter in (
        #     SolarPositionParameter.event_type,
        #     SolarPositionParameter.event_time,
        # ):
        #     # For event_time: dtype datetime64, for event_type: object dtype
        #     # Check if any entry is not None/NaT
        #     has_data = any(
        #         (v is not None and not (isinstance(v, datetime64) and numpy.isnat(v)))
        #         for v in value
        #     )
        #     if not has_data:
        #         continue  # skip entirely

        from numpy import datetime64, isnat
        if parameter in (
            SolarPositionParameter.event_type,
            SolarPositionParameter.event_time,
        ):
            # If value is None, there is no event array at all—skip
            if value is None:
                continue

            # For event_time: dtype datetime64, for event_type: object dtype/SolarEvent
            # If value is not an array, make it a list so iteration succeeds
            if not hasattr(value, "__iter__") or isinstance(value, str):
                value_list = [value]
            else:
                value_list = value

            def is_real_event(ev):
                # For datetime columns (event_time)
                if isinstance(ev, datetime64):
                    return not isnat(ev)
                # For event_type columns
                if ev is not None and hasattr(ev, "name") and ev.name == "none":
                    return False
                return ev not in (None, "None")

            has_data = any(is_real_event(v) for v in value_list)
            if not has_data:
                continue  # skip entirely

        table.add_column(header)

    return table


def populate_solar_position_table(
    table: Table,
    model_result: dict,
    timestamps,
    index: bool,
    rounding_places: int,
    # position_parameters: Sequence[SolarPositionParameter],
    sparkline: bool = False,
):
    """
    Populates a Rich Table with solar position data
    using the already-built table structure (columns).
    Compatible with flattened model_result dictionaries.
    """
    from numpy import datetime64, bool_

    for idx, timestamp in enumerate(timestamps):
        row = []
        if index:
            row.append(str(idx + 1))
        row.append(to_datetime(timestamp).strftime("%Y-%m-%d %H:%M:%S"))

        # Iterate over each table column (already reflecting the final structure)
        for column in table.columns:
            header = column.header
            if header in ("Index", "Time"):
                continue

            # Retrieve matching array from model_result
            value_array = model_result.get(header)
            if value_array is None or len(value_array) <= idx:
                row.append("")
                continue

            value = get_scalar(value_array, idx, rounding_places)

            # Format final cell output
            if value is None:
                row.append("")

            elif isinstance(value, SolarEvent):
                row.append(format_string(value.value))

            elif isinstance(value, str):
                vl = value.lower()
                style = {
                    "above": "bold yellow",
                    "low angle": "dark_orange",
                    "below": "red",
                }.get(vl)
                row.append(Text(value, style=style) if style else value)

            elif isinstance(value, datetime64):
                if isna(value):
                    row.append("")
                else:
                    dt = value.astype("datetime64[s]").astype("O")
                    row.append(str(dt.time()))

            elif isinstance(value, bool_) or isinstance(value, bool):
                # bool _must_ come before numeric !
                row.append(str(bool(value)))

            elif isinstance(value, (int, float, numpy.generic)):
                rounded = str(round_float_values(value, rounding_places))

                style = "bold cyan"
                if value < 0:
                    style = "bold red"
                elif value == 0:
                    style = "highlight dim"
                row.append(Text(rounded, style=style))

            else:
                row.append(str(value))

        table.add_row(*row)

    if sparkline:
        # Build a footer row of sparklines (or blank) for each column
        footer_cells = []
        for column in table.columns:
            header = column.header

            # Keep index/time columns blank
            if header in ("Index", "Time"):
                # footer_cells.append("")
                footer_cells.append("Sparkline")
                continue

            # Retrieve the full series for this column
            series = model_result.get(header)
            if series is None or len(series) == 0:
                footer_cells.append("")
                continue

            # Only numeric series get sparklines
            # Skip booleans, strings, events, datetimes
            if not isinstance(series, (list, tuple)) and hasattr(series, "dtype"):
                dtype = series.dtype
            else:
                footer_cells.append("")
                continue

            if dtype.kind in ("i", "u", "f"):
                # Generate sparkline: pass the raw numpy array and timestamps
                from pvgisprototype.cli.print.sparklines import (
                    convert_series_to_sparkline,
                )

                spark = convert_series_to_sparkline(
                    series=series,
                    timestamps=timestamps,
                    frequency=timestamps.freq,
                )
                footer_cells.append(Text(spark, style="dim"))
            else:
                footer_cells.append("")

        # Add the sparkline footer as a final row
        table.add_row(*footer_cells)

    return table


def print_solar_position_table_and_metadata_panels(
    time,
    caption,
    table,
    legend,
    fingerprint,
    subtitle_caption="Reference",
    subtitle_legend="Legend",
):
    """ """
    console = Console()
    console.print(table)

    panels = []

    if time:
        panels.append(
            time,
        )

    if caption:
        panels.append(
            Panel(
                caption,
                subtitle=f"[gray]{subtitle_caption}[/gray]",
                subtitle_align="right",
                border_style="dim",
                expand=False,
            )
        )

    if legend:
        panels.append(
            Panel(
                legend,
                subtitle=f"[dim]{subtitle_legend}[/dim]",
                subtitle_align="right",
                border_style="dim",
                # style="dim",
                expand=False,
                padding=(0, 1),
            )
        )

    if panels:
        console.print(Columns(panels))

    if fingerprint:  # version & fingerprint
        console.print(fingerprint)
