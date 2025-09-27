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
from pvgisprototype import PhotovoltaicPower
from rich.table import Table
from rich.panel import Panel


def build_photovoltaic_module_table() -> Table:
    """ """
    photovoltaic_module_table = Table(
        box=None,
        show_header=True,
        header_style=None,
        show_edge=False,
        pad_edge=False,
    )
    photovoltaic_module_table.add_column("Tech", justify="right", style="bold")
    photovoltaic_module_table.add_column("Peak-Power", justify="center", style="bold")
    photovoltaic_module_table.add_column("Mount Type", justify="left", style="bold")

    return photovoltaic_module_table


def populate_photovoltaic_module_table(
    table: Table,
    photovoltaic_power: PhotovoltaicPower,
) -> Table:
    """ """
    photovoltaic_module, mount_type = photovoltaic_power.technology.split(":")
    # peak_power_unit = photovoltaic_power.presentation.peak_power_unit
    peak_power_unit = "Peak Power Unit"
    table.add_row(
        photovoltaic_module,
        f"[green]{photovoltaic_power.peak_power}[/green] {peak_power_unit}",
        mount_type,
    )

    return table


def build_photovoltaic_module_panel(photovoltaic_module_table) -> Panel:
    """ """
    photovoltaic_module_panel = Panel(
        photovoltaic_module_table,
        subtitle="PV Module",
        subtitle_align="right",
        safe_box=True,
        expand=True,
        padding=(0, 2),
    )

    return photovoltaic_module_panel
