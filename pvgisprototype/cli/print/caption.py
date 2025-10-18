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
from pvgisprototype.cli.print.flat import flatten_dictionary
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import (
    ANGLE_UNITS_COLUMN_NAME,
    ELEVATION_COLUMN_NAME,
    LATITUDE_COLUMN_NAME,
    LONGITUDE_COLUMN_NAME,
    MEAN_PHOTOVOLTAIC_POWER_NAME,
    NOT_AVAILABLE,
    ROUNDING_PLACES_DEFAULT,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_NAME,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_NAME,
    TIME_ALGORITHM_NAME,
    UNIT_NAME,
    UNITLESS,
)


def build_simple_caption(
    longitude,
    latitude,
    rounded_table,
    timezone,
    user_requested_timezone,
    minimum_value=None,
    maximum_value=None,
):
    """
    Notes
    -----
    Add the surface orientation and tilt only if they exist in the input
    `rounded_table` !

    """
    caption = (
        f"[underline]Position[/underline]  "
        + (
            f"Orientation : [bold blue]{rounded_table.get(SURFACE_ORIENTATION_NAME).value}[/bold blue], "
            if rounded_table.get(SURFACE_ORIENTATION_NAME) is not None
            else ""
        )
        + (
            f"Tilt : [bold blue]{rounded_table.get(SURFACE_TILT_NAME).value}[/bold blue] "
            if rounded_table.get(SURFACE_TILT_NAME) is not None
            else ""
        )
        + f"\n[underline]Location[/underline]  "
        + (
            f"{LONGITUDE_COLUMN_NAME}, {LATITUDE_COLUMN_NAME} = [bold]{longitude}[/bold], [bold]{latitude}[/bold], "
        )
        + f"[dim]{rounded_table.get(UNIT_NAME, UNITLESS)}[/dim]"
        f"\n[underline]{MEAN_PHOTOVOLTAIC_POWER_NAME}[/underline]  "
        + f"[bold blue]{rounded_table.get(MEAN_PHOTOVOLTAIC_POWER_NAME)}[/bold blue] "
        f"\n[underline]Algorithms[/underline]  "  # ---------------------------
        f"Timing : [bold]{rounded_table.get(TIME_ALGORITHM_NAME, NOT_AVAILABLE)}[/bold], "
    )

    if user_requested_timezone is not None and user_requested_timezone != ZoneInfo(
        "UTC"
    ):
        caption += f"Local Zone : [bold]{user_requested_timezone}[/bold], "
    else:
        caption += f"Zone : [bold]{timezone}[/bold], "

    if minimum_value:
        caption += f"Minimum : {minimum_value}"

    if maximum_value:
        caption += f"Minimum : {maximum_value}"

    return caption


def build_caption(
    data_dictionary,
    longitude,
    latitude,
    elevation=None,
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    surface_orientation=True,
    surface_tilt=True,
    minimum_value=None,
    maximum_value=None,
):
    """Build the _main_ caption for a solar position tabular output.

    Include :

       - Location
         - Longitude ϑ
         - Latitude ϕ
         - Elevation + Unit

       - Position
         - Surface Orientation ↻
         - Surface Tilt ⦥
         - Angular units

    Notes
    -----
    Add the surface orientation and tilt only if they exist in the input
    `data_dictionary` !

    """
    # Collect items from `data_dictionary`
    first_model = next(iter(data_dictionary))
    data_dictionary = flatten_dictionary(data_dictionary[first_model])

    surface_orientation = round_float_values(
        (
            data_dictionary.get(SURFACE_ORIENTATION_COLUMN_NAME, None)
            if surface_orientation
            else ""
        ),
        rounding_places,
    )
    surface_tilt = round_float_values(
        (
            data_dictionary.get(SURFACE_TILT_COLUMN_NAME, None)
            if surface_tilt
            else None
        ),
        rounding_places,
    )
    angular_units = data_dictionary.get(ANGLE_UNITS_COLUMN_NAME, UNITLESS)

    # Build caption

    caption = str()

    # Location
    if longitude or latitude or elevation:
        caption += "[underline]Location[/underline]  "

    ## Longitude ϑ
    ## Latitude ϕ
    if longitude and latitude:
        caption += f"{LONGITUDE_COLUMN_NAME}, {LATITUDE_COLUMN_NAME} = [bold]{longitude}[/bold], [bold]{latitude}[/bold]"

    ## Angular units
    if (
        longitude
        or latitude
        or elevation
        or surface_orientation
        # or rear_side_surface_orientation
        or surface_tilt
        # or rear_side_surface_tilt
        and angular_units is not None
    ):
        caption += f"  [underline]Angular units[/underline] [dim][code]{angular_units}[/code][/dim]"

    ## Elevation + Unit
    if elevation:
        caption += f"{ELEVATION_COLUMN_NAME}: [bold]{elevation}[/bold]\n"

    # Position
    caption += f"\n[underline]Position[/underline]  "

    ## Surface Orientation ↻
    if surface_orientation is not None:
        caption += (
            f"{SURFACE_ORIENTATION_COLUMN_NAME}: [bold]{surface_orientation}[/bold], "
        )
    ## Surface Tilt ⦥
    if surface_tilt is not None:
        caption += f"{SURFACE_TILT_COLUMN_NAME}: [bold]{surface_tilt}[/bold] "

    # What is this required for ? --------------------------------------------
    if minimum_value:
        caption += f"Minimum : {minimum_value}"

    if maximum_value:
        caption += f"Minimum : {maximum_value}"

    return caption
