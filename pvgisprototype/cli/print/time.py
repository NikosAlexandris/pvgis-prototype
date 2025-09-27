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
from rich.panel import Panel
from rich.table import Table

from pvgisprototype.cli.print.helpers import infer_frequency_from_timestamps


def build_time_table() -> Table:
    """ """
    time_table = Table(
        box=None,
        show_header=True,
        header_style=None,
        show_edge=False,
        pad_edge=False,
    )
    time_table.add_column("Start", justify="left", style="bold")
    time_table.add_column("Every", justify="left", style="dim bold")
    time_table.add_column("End", justify="left", style="dim bold")
    time_table.add_column("Zone", justify="left", style="dim bold")

    return time_table


def populate_time_table(
        table: Table,
        timestamps: DatetimeIndex,
        timezone: ZoneInfo,
        ) -> Table:
    """
    """
    frequency, frequency_label = infer_frequency_from_timestamps(timestamps)
    table.add_row(
        str(timestamps.strftime("%Y-%m-%d %H:%M").values[0]),
        str(frequency) if frequency and frequency != 'Single' else '-',
        str(timestamps.strftime("%Y-%m-%d %H:%M").values[-1]),
        str(timezone),
    )

    return table


def build_time_panel(
    time_table,
    safe_box: bool = True,
    expand: bool = False,
    padding: tuple = (0, 2),
) -> Panel:
    """ """
    return Panel(
        time_table,
        # title="Time",
        # subtitle="Time",
        # subtitle_align="right",
        safe_box=safe_box,
        border_style="dim",
        expand=expand,
        padding=padding,
    )
