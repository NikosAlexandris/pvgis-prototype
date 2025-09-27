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
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import (
    UNIT_NAME,
    ELEVATION_NAME,
    LATITUDE_NAME,
    LONGITUDE_NAME,
    ORIENTATION_NAME,
    TILT_NAME,
    INCIDENCE_DEFINITION,
    SURFACE_ORIENTATION_NAME,
    SURFACE_TILT_NAME,
)


def build_position_table() -> Table:
    """ """
    position_table = Table(
        box=None,
        show_header=True,
        header_style="bold dim",
        show_edge=False,
        pad_edge=False,
    )
    position_table.add_column(
        f"{LATITUDE_NAME}", justify="center", style="bold", no_wrap=True
    )
    position_table.add_column(
        f"{LONGITUDE_NAME}", justify="center", style="bold", no_wrap=True
    )
    position_table.add_column(
        f"{ELEVATION_NAME}", justify="center", style="bold", no_wrap=True
    )
    position_table.add_column(
        f"{ORIENTATION_NAME}", justify="center", style="bold", no_wrap=True
    )
    position_table.add_column(
        f"{TILT_NAME}", justify="center", style="bold", no_wrap=True
    )
    position_table.add_column(
        f"{UNIT_NAME}", justify="center", style="dim", no_wrap=True
    )

    return position_table


def populate_position_table(
    table: Table,
    data_model: PhotovoltaicPower,  # can this become a generic data model ?
    latitude: float,
    longitude: float,
    elevation: float,
    surface_orientation: bool | float = True,
    surface_tilt: bool | float = True,
    rounding_places: int = 3,
) -> Table:
    """
    Populate the 'position' table for a photovoltaic module using attributes
    from the input data model which must contain the _positional_ input
    parameters of the function described under Parameters :

    Parameters
    ----------
    - latitude
    - longitude
    - elevation
    - surface_orientation
    - surface_tilt

    Returns
    -------
    table: Table

    """
    latitude = round_float_values(
        latitude, rounding_places
    )  # rounding_places)
    # position_table.add_row(f"{LATITUDE_NAME}", f"[bold]{latitude}[/bold]")

    longitude = round_float_values(
        longitude, rounding_places
    )  # rounding_places)

    # surface_orientation: float | None = (
    #     dictionary.get(SURFACE_ORIENTATION_COLUMN_NAME, None)
    #     if surface_orientation
    #     else None
    # )
    # surface_orientation: float = round_float_values(
    #     surface_orientation, rounding_places
    # )
    # surface_orientation: float | None = dictionary.get(SURFACE_ORIENTATION_COLUMN_NAME)
    if surface_orientation:
        surface_orientation = data_model.surface_orientation
    if surface_orientation is not None:
        surface_orientation = round_float_values(
            surface_orientation, rounding_places
        )

    # Get and round surface_tilt if it's not None
    # surface_tilt: float | None = (
    #     dictionary.get(SURFACE_TILT_COLUMN_NAME, None) if surface_tilt else None
    # )
    # surface_tilt: float = round_float_values(surface_tilt, rounding_places)
    # surface_tilt: float | None = dictionary.get(SURFACE_TILT_COLUMN_NAME)
    if surface_tilt:
        surface_tilt = data_model.surface_tilt
    if surface_tilt is not None:
        surface_tilt = round_float_values(surface_tilt, rounding_places)

    table.add_row(
        f"{latitude}",
        f"{longitude}",
        f"{elevation}",
        f"{surface_orientation}",
        f"{surface_tilt}",
        f"{data_model.solar_incidence.unit}",
    )
    # position_table.add_row("Time :", f"{timestamp[0]}")
    # position_table.add_row("Time zone :", f"{timezone}")

    longest_label_length = max(len(key) for key in data_model.to_dictionary().keys())
    surface_position_keys = {
        SURFACE_ORIENTATION_NAME,
        SURFACE_TILT_NAME,
        # ANGLE_UNIT_NAME,
        # INCIDENCE_DEFINITION,
        # UNIT_NAME,
    }
    for key, value in data_model.output.items():
        if key in surface_position_keys:
            padded_key = f"{key} :".ljust(longest_label_length + 3, " ")
            if key == INCIDENCE_DEFINITION:
                value = f"[yellow]{value}[/yellow]"
            table.add_row(padded_key, str(value))

    return table


def build_position_panel(position_table, width) -> Panel:
    """ """
    return Panel(
        position_table,
        # title="Positioning",  # Add title to provide context without being too bold
        # title_align="left",  # Align the title to the left
        subtitle="Solar Surface",
        subtitle_align="right",
        # box=None,
        safe_box=True,
        style="",
        border_style="dim",  # Soften the panel with a dim border style
        # expand=False,
        # expand=True,
        padding=(0, 2),
        width=width,
    )
