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
from pvgisprototype.cli.print.fingerprint import retrieve_fingerprint
from pvgisprototype.cli.print.flat import flatten_dictionary
from pvgisprototype.cli.print.position.caption import build_solar_position_model_caption
from pvgisprototype.cli.print.getters import get_value_or_default, get_scalar
from pvgisprototype.cli.print.helpers import infer_frequency_from_timestamps
from pvgisprototype.cli.print.position.table import (
    build_solar_position_table,
    populate_solar_position_table,
    print_solar_position_table_and_metadata_panels,
)
from pvgisprototype.cli.print.time import build_time_table, build_time_panel
from pvgisprototype.cli.print.caption import build_caption
from pvgisprototype.cli.print.panels import build_version_and_fingerprint_columns
from typing import Sequence
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.columns import Columns
from rich.box import HORIZONTALS, ROUNDED
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.cli.print.legend import build_legend_table
from zoneinfo import ZoneInfo
from pvgisprototype.api.position.models import (
    SolarPositionParameter,
)
from pvgisprototype.constants import (
    ALTITUDE_COLUMN_NAME,
    ANGLE_UNIT_NAME,
    AZIMUTH_COLUMN_NAME,
    AZIMUTH_ORIGIN_NAME,
    DECLINATION_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    HOUR_ANGLE_COLUMN_NAME,
    INCIDENCE_DEFINITION,
    INCIDENCE_COLUMN_NAME,
    LATITUDE_COLUMN_NAME,
    LOCAL_TIME_COLUMN_NAME,
    LONGITUDE_COLUMN_NAME,
    POSITIONING_ALGORITHM_NAME,
    ROUNDING_PLACES_DEFAULT,
    SOLAR_EVENT_COLUMN_NAME,
    SOLAR_EVENT_TIME_COLUMN_NAME,
    SURFACE_ORIENTATION_NAME,
    SURFACE_TILT_NAME,
    SYMBOL_MEAN,
    SYMBOL_SUMMATION,
    TIME_COLUMN_NAME,
    UNIT_NAME,
    ZENITH_COLUMN_NAME,
)

console = Console()


def print_solar_position_table_panels(
    longitude,
    latitude,
    timestamp,
    timezone,
    solar_position_table,
    rounding_places=ROUNDING_PLACES_DEFAULT,
    position_parameters=SolarPositionParameter.all,
    surface_orientation=True,
    surface_tilt=True,
    user_requested_timestamp=None,
    user_requested_timezone=None,
) -> None:
    """
    """
    first_model = solar_position_table[next(iter(solar_position_table))]
    panels = []

    # surface position Panel
    table = Table(box=None, show_header=False, show_edge=False, pad_edge=False)
    table.add_column(justify="right", style="none", no_wrap=True)
    table.add_column(justify="left")
    table.add_row(f"{LATITUDE_COLUMN_NAME} :", f"[bold]{latitude}[/bold]")
    table.add_row(f"{LONGITUDE_COLUMN_NAME} :", f"[bold]{longitude}[/bold]")
    table.add_row("Time :", f"{timestamp[0]}")
    table.add_row("Time zone :", f"{timezone}")
    longest_label_length = max(len(key) for key in first_model.keys())
    surface_position_keys = {
        SURFACE_ORIENTATION_NAME,
        SURFACE_TILT_NAME,
        ANGLE_UNIT_NAME,
        INCIDENCE_DEFINITION,
        UNIT_NAME,
    }
    for key, value in first_model.items():
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

    # solar position Panel/s
    for model_result in solar_position_table.values():
        table = Table(box=None, show_header=False, show_edge=False, pad_edge=False)
        table.add_column(justify="right", style="none", no_wrap=True)
        table.add_column(justify="left")

        longest_label_length = max(len(key) for key in model_result.keys())
        _index = 0

        position_parameter_values = {
            SolarPositionParameter.declination: lambda idx=_index: get_scalar(
                get_value_or_default(model_result, DECLINATION_COLUMN_NAME),
                idx,
                rounding_places,
            ),
            # SolarPositionParameter.timing: lambda idx=_index: str(get_value_or_default(
            #     model_result, TIME_ALGORITHM_NAME
            # )),
            # SolarPositionParameter.positioning: lambda idx=_index: str(get_value_or_default(
            #     model_result, POSITIONING_ALGORITHM_NAME
            # )),
            SolarPositionParameter.hour_angle: lambda idx=_index: get_scalar(
                get_value_or_default(model_result, HOUR_ANGLE_COLUMN_NAME),
                idx,
                rounding_places,
            ),
            SolarPositionParameter.zenith: lambda idx=_index: get_scalar(
                get_value_or_default(model_result, ZENITH_COLUMN_NAME),
                idx,
                rounding_places,
            ),
            SolarPositionParameter.altitude: lambda idx=_index: get_scalar(
                get_value_or_default(model_result, ALTITUDE_COLUMN_NAME, None),
                idx,
                rounding_places,
            ),
            SolarPositionParameter.azimuth: lambda idx=_index: get_scalar(
                get_value_or_default(model_result, AZIMUTH_COLUMN_NAME),
                idx,
                rounding_places,
            ),
            SolarPositionParameter.incidence: lambda idx=_index: get_scalar(
                get_value_or_default(model_result, INCIDENCE_COLUMN_NAME),
                idx,
                rounding_places,
            ),
            SolarPositionParameter.event_time: lambda idx=_index: get_scalar(
                get_value_or_default(model_result, SOLAR_EVENT_TIME_COLUMN_NAME),
                idx,
                rounding_places,
            ),
            SolarPositionParameter.event_type: lambda idx=_index: get_scalar(
                get_value_or_default(model_result, SOLAR_EVENT_COLUMN_NAME),
                idx,
                rounding_places,
            ),
        }
        for parameter in position_parameters:
            if parameter in position_parameter_values:
                padded_key = f"{parameter.value} :".ljust(longest_label_length + 1, " ")
                value = position_parameter_values[parameter]()
                if parameter == AZIMUTH_ORIGIN_NAME:
                    value = f"[yellow]{value}[/yellow]"
                table.add_row(padded_key, str(value))

        title = f"[bold]{get_value_or_default(model_result, POSITIONING_ALGORITHM_NAME)}[/bold]"
        panel = Panel(
            table,
            title=title,
            box=ROUNDED,
            # style=panel_style,
            padding=(0, 2),
        )
        panels.append(panel)

    columns = Columns(panels, expand=True, equal=True, padding=2)
    console.print(columns)


def print_solar_position_series_table(
    longitude,
    latitude,
    timestamps,
    timezone,
    table,
    position_parameters: Sequence[SolarPositionParameter] = SolarPositionParameter.all,
    title="Solar position overview",
    index: bool = False,
    version: bool = False,
    fingerprint: bool = False,
    surface_orientation=None,
    surface_tilt=None,
    incidence=None,
    user_requested_timestamps=None,
    user_requested_timezone=None,
    rounding_places=ROUNDING_PLACES_DEFAULT,
    group_models=False,
    panels=False,
) -> None:
    """ """
    rounded_table = round_float_values(table, rounding_places)

    if panels:
        if timestamps.size == 1:
            print_solar_position_table_panels(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamps,
                timezone=timezone,
                solar_position_table=rounded_table,
                position_parameters=position_parameters,
                rounding_places=rounding_places,
                user_requested_timestamp=user_requested_timestamps,
                user_requested_timezone=user_requested_timezone,
            )
    else:
        longitude = round_float_values(longitude, rounding_places)
        latitude = round_float_values(latitude, rounding_places)

        # Build the main caption

        caption = build_caption(
            data_dictionary=rounded_table,
            longitude=longitude,
            latitude=latitude,
            # elevation=elevation,
            rounding_places=rounding_places,
            surface_orientation=True,
            surface_tilt=True,
        )

        # Iterate over multiple solar position models -- we _can_ have many !

        for _, model_result in rounded_table.items():
            if model_result:
                model_result = flatten_dictionary(model_result)

                # Update the caption with model-specific metadata

                model_caption = build_solar_position_model_caption(
                    solar_position_model_data=model_result,
                    caption=caption,
                    timezone=timezone,
                    user_requested_timezone=user_requested_timezone,
                )

                # then : Create a Legend table for the symbols in question

                legend = build_legend_table(
                    dictionary=model_result,
                    caption=model_caption,
                    show_header=False,
                    box=None,
                )

                # Time might be Local 

                if user_requested_timestamps is not None:
                    time_column_name = LOCAL_TIME_COLUMN_NAME
                else:
                    time_column_name = TIME_COLUMN_NAME

                if timestamps is not None:
                    if user_requested_timezone is not None:
                        if user_requested_timezone != ZoneInfo("UTC"):
                            time_column_name = LOCAL_TIME_COLUMN_NAME
                            timezone_string = f"Local Zone: [bold]{timezone}[/bold]"
                        else:
                            time_column_name = TIME_COLUMN_NAME

                if timezone:
                    if timezone == ZoneInfo('UTC'):
                        timezone_string = f"[bold]{timezone}[/bold]"
                    else:
                        timezone_string = f"Local Zone: [bold]{timezone}[/bold]"

                # Build solar position table structure

                solar_position_table = build_solar_position_table(
                    title=title,
                    index=index,
                    input_table=rounded_table,
                    dictionary=model_result,
                    position_parameters=position_parameters,
                    # timestamps=timestamps,
                    # rounding_places=rounding_places,
                    time_column_name=time_column_name,
                    time_column_footer=f"{SYMBOL_SUMMATION} / [blue]{SYMBOL_MEAN}[/blue]",  # Abusing this "cell" as a "Row Name"
                    time_column_footer_style="purple",  # to make it somehow distinct from the Column !
                    # keys_to_sum = KEYS_TO_SUM,
                    # keys_to_average = KEYS_TO_AVERAGE,
                    # keys_to_exclude = KEYS_TO_EXCLUDE,
                )

                # -------------------------------------------------- Ugly Hack ---
                if user_requested_timestamps is not None:
                    timestamps = user_requested_timestamps
                # --- Ugly Hack --------------------------------------------------

                output_table = populate_solar_position_table(
                    table=solar_position_table,
                    model_result=model_result,
                    timestamps=timestamps,
                    index=index,
                    rounding_places=rounding_places,
                )

                # Create Panels for time, caption and legend

                time_table = build_time_table()
                frequency, frequency_label = infer_frequency_from_timestamps(timestamps)
                time_table.add_row(
                    str(timestamps.strftime("%Y-%m-%d %H:%M").values[0]),
                    str(frequency) if frequency and frequency != "Single" else "-",
                    str(timestamps.strftime("%Y-%m-%d %H:%M").values[-1]),
                    str(timezone_string),
                )
                time_panel = build_time_panel(time_table, padding=(0, 1, 2, 1))

                # Version & Fingerprint

                fingerprint = retrieve_fingerprint(dictionary=model_result)
                version_and_fingerprint_and_column = (
                    build_version_and_fingerprint_columns(
                        version=version,
                        fingerprint=fingerprint,
                    )
                )

                # if verbose:  # Print if requested via at least 1x `-v` ?
                print_solar_position_table_and_metadata_panels(
                    time=time_panel,
                    caption=model_caption,
                    table=output_table,
                    legend=legend,
                    fingerprint=version_and_fingerprint_and_column,
                )


def print_solar_position_series_in_columns(
    longitude,
    latitude,
    timestamps,
    timezone,
    table,
    rounding_places=ROUNDING_PLACES_DEFAULT,
    index: bool = False,
):
    """ """
    panels = []

    # Iterating through each timestamp
    for i, timestamp in enumerate(timestamps):
        table_panel = Table(title=f"Time: {timestamp}", box=ROUNDED)
        table_panel.add_column("Parameter", justify="right")
        table_panel.add_column("Value", justify="left")

        # Optionally add an index column
        if index:
            table_panel.add_column("Index", style="dim")
            table_panel.add_row("Index", str(i))

        # Add longitude, latitude, and other non-time-varying parameters
        table_panel.add_row("Longitude", str(longitude))
        table_panel.add_row("Latitude", str(latitude))

        # For each parameter of interest, aggregate across models for this timestamp
        parameters = [
            "Declination",
            "Hour Angle",
            "Zenith",
            "Altitude",
            "Azimuth",
            "Incidence",
        ]
        for param in parameters:
            # Assume `table` is a dictionary of models, each containing a list of values for each parameter
            values = [
                round_float_values(model_result[param][i], rounding_places)
                for _, model_result in table.items()
                if param in model_result
            ]
            value_str = ", ".join(map(str, values))  # Combine values from all models
            table_panel.add_row(param, value_str)

        panel = Panel(table_panel, expand=True)
        panels.append(panel)

    console.print(Columns(panels))
