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
from rich import print
from pandas import isna
from pvgisprototype.cli.print.getters import get_event_time_value, get_value_or_default, get_scalar
from pvgisprototype.cli.print.helpers import infer_frequency_from_timestamps
from pvgisprototype.cli.print.irradiance.text import format_string
from pvgisprototype.cli.print.time import build_time_table, build_time_panel
from pvgisprototype.cli.print.caption import build_caption
from pvgisprototype.cli.print.panels import build_version_and_fingerprint_columns
from typing import Sequence
from numpy import datetime64
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.columns import Columns
from rich.box import HORIZONTALS, ROUNDED, SIMPLE_HEAD
from rich.text import Text
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.cli.print.legend import build_legend_table
from zoneinfo import ZoneInfo
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_PARAMETER_COLUMN_NAMES,
    SolarPositionParameter,
)
from pvgisprototype.constants import (
    ALTITUDE_COLUMN_NAME,
    ANGLE_UNIT_NAME,
    AZIMUTH_COLUMN_NAME,
    AZIMUTH_ORIGIN_NAME,
    DECLINATION_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_NAME,
    HORIZON_HEIGHT_COLUMN_NAME,
    HOUR_ANGLE_COLUMN_NAME,
    INCIDENCE_ALGORITHM_NAME,
    INCIDENCE_DEFINITION,
    INCIDENCE_COLUMN_NAME,
    LATITUDE_COLUMN_NAME,
    LOCAL_TIME_COLUMN_NAME,
    LONGITUDE_COLUMN_NAME,
    NOT_AVAILABLE,
    POSITIONING_ALGORITHM_NAME,
    ROUNDING_PLACES_DEFAULT,
    SHADING_ALGORITHM_NAME,
    SOLAR_EVENT_COLUMN_NAME,
    SOLAR_EVENT_TIME_COLUMN_NAME,
    SUN_HORIZON_NAME,
    SURFACE_ORIENTATION_NAME,
    SURFACE_TILT_NAME,
    TIME_COLUMN_NAME,
    UNIT_NAME,
    VISIBLE_COLUMN_NAME,
    ZENITH_COLUMN_NAME,
)
from pvgisprototype.log import logger

console = Console()


# position.py (add this once)
SOLAR_POSITION_OUTPUT_MAP = {
    SolarPositionParameter.altitude: ("Solar Altitude", "value"),
    SolarPositionParameter.zenith: ("Solar Zenith", "value"),
    SolarPositionParameter.azimuth: ("Solar Azimuth", "value"),
    SolarPositionParameter.declination: ("Solar Declination", "value"),
    SolarPositionParameter.hour_angle: ("Hour Angle", "value"),
    SolarPositionParameter.incidence: ("Solar Incidence", "value"),
    SolarPositionParameter.horizon: ("Horizon Height", "value"),
    SolarPositionParameter.sun_horizon: ("Sun Horizon Position", "value"),
    SolarPositionParameter.visible: ("Visible", "value"),
    SolarPositionParameter.event_type: ("Solar Event", "value"),
    SolarPositionParameter.event_time: ("Solar Event", "value"),
}
SOLAR_POSITION_PARAMETER_SECTION_NAMES = {
    SolarPositionParameter.altitude: "Solar Altitude",
    SolarPositionParameter.zenith: "Solar Zenith",
    SolarPositionParameter.declination: "Solar Declination",
    SolarPositionParameter.hour_angle: "Hour Angle",
    SolarPositionParameter.azimuth: "Solar Azimuth",
    SolarPositionParameter.incidence: "Solar Incidence",
    SolarPositionParameter.horizon: "Horizon Height",
    SolarPositionParameter.sun_horizon: "Sun Horizon Position",
    SolarPositionParameter.visible: "Visible",
    SolarPositionParameter.event_type: "Solar Event",
    SolarPositionParameter.event_time: "Solar Event",
    # Add others as needed
}


def get_section_field_value(model_result, section_name, field_prefix):
    section = model_result.get(section_name, {})
    for key, value in section.items():
        if key.startswith(field_prefix):
            return value
    return None

def retrieve_key_value(
    dictionary: dict, key: str,
) -> bool:
    """
    Recursively search for the fingerprint key in a nested dictionary.
    """
    if isinstance(dictionary, dict):
        if key in dictionary:
            logger.info(f"Found the key {key=}")
            return True

        # Recursively search each value of the dictionary
        return any(retrieve_key_value(value, key) for value in dictionary.values())

    # else:
    #     logger.debug(f"Did not find the {key=} in the input data structure {dictionary=} !")
    #     return False


def extract_altitude_value(model_result):
    # Find the 'Solar Altitude' section
    section = model_result.get('Solar Altitude', {})
    # Find the key that contains 'Altitude' (could be 'Altitude ⦩', etc.)
    for key, value in section.items():
        if 'Altitude' in key:
            return value
    return None  # or NOT_AVAILABLE


def get_section_field_and_value(model_result, section_name, column_name):
    """
    Returns (field_name, value) for the first field in section_name that starts with column_name.
    """
    section = model_result.get(section_name, {})
    for key, value in section.items():
        if key.startswith(column_name):
            return key, value
    return None, None


def find_nested_key(data, search_key):
    """Recursively search for a key in nested dictionaries/lists"""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == search_key:
                return value
            result = find_nested_key(value, search_key)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_nested_key(item, search_key)
            if result is not None:
                return result
    return None



def get_parameter_value(model_result, parameter):
    section_field = SOLAR_POSITION_OUTPUT_MAP.get(parameter)
    if not section_field:
        return None  # Or NOT_AVAILABLE
    section, field = section_field
    section_data = model_result.get(section)
    if section_data is None:
        return None  # Or NOT_AVAILABLE
    if field is None:
        return section_data  # For overview or composite sections
    return section_data.get(field, None)


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
    """ """
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
                get_value_or_default(model_result,
                                     DECLINATION_COLUMN_NAME),
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
                get_value_or_default(model_result,
                                     HOUR_ANGLE_COLUMN_NAME),
                idx,
                rounding_places,
            ),
            SolarPositionParameter.zenith: lambda idx=_index: get_scalar(
                get_value_or_default(model_result,
                                     ZENITH_COLUMN_NAME), idx, rounding_places
            ),
            SolarPositionParameter.altitude: lambda idx=_index: get_scalar(
                get_value_or_default(model_result,
                                     ALTITUDE_COLUMN_NAME, None), idx, rounding_places
            ),
            SolarPositionParameter.azimuth: lambda idx=_index: get_scalar(
                get_value_or_default(model_result,
                                     AZIMUTH_COLUMN_NAME), idx, rounding_places
            ),
            SolarPositionParameter.incidence: lambda idx=_index: get_scalar(
                get_value_or_default(model_result,
                                     INCIDENCE_COLUMN_NAME),
                idx,
                rounding_places,
            ),
            SolarPositionParameter.event_time: lambda idx=_index: get_scalar(
                get_value_or_default(model_result,
                                     SOLAR_EVENT_TIME_COLUMN_NAME),
                idx,
                rounding_places,
            ),
            SolarPositionParameter.event_type: lambda idx=_index: get_scalar(
                get_value_or_default(model_result,
                                     SOLAR_EVENT_COLUMN_NAME),
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
    """
    """
    rounded_table = round_float_values(table, rounding_places)
    # print(f"Rounded table :\n\n   {rounded_table=}")
    # print("")

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
        first_model = rounded_table[next(iter(rounded_table))]
        # print(f"First model :\n\n   {first_model=}")

        columns = []
        if index:
            columns.append("Index")
        if user_requested_timestamps is not None:
            time_column_name = LOCAL_TIME_COLUMN_NAME
        else:
            time_column_name = TIME_COLUMN_NAME
        if timestamps is not None:
            if user_requested_timezone != ZoneInfo('UTC'):
                time_column_name = LOCAL_TIME_COLUMN_NAME
            else:
                time_column_name = TIME_COLUMN_NAME
            columns.append(time_column_name)

        # for parameter in position_parameters:
        #     print(f"> Parameter :\n\n   {parameter=}\n\n   {parameter.name=}")
        #     # Assuming all "models" contain the same keys ! ----------------------
        #     # print(f"{rounded_table=}")
        #     if parameter in SOLAR_POSITION_PARAMETER_COLUMN_NAMES and retrieve_key_value(rounded_table, parameter.name):
        #         print(f"   + YES in column names")
        #         column = SOLAR_POSITION_PARAMETER_COLUMN_NAMES[parameter]
        #         if isinstance(column, list):
        #             columns.extend(column)
        #         else:
        #             columns.append(column)

        for parameter in position_parameters:
            section_name = SOLAR_POSITION_PARAMETER_SECTION_NAMES.get(parameter)
            column_name = SOLAR_POSITION_PARAMETER_COLUMN_NAMES.get(parameter)
            field_name, _ = get_section_field_and_value(first_model, section_name, column_name)
            columns.append(field_name or column_name)

        # print(f"Columns :\n\n   {columns=}")


        # Caption

        ## Position

        caption = build_caption(
            longitude, latitude, rounded_table, timezone, user_requested_timezone
        )

        for _, model_result in rounded_table.items():
            if model_result:
                model_caption = caption

                solar_positioning_algorithm = get_value_or_default(
                    model_result, POSITIONING_ALGORITHM_NAME, NOT_AVAILABLE
                )
                model_caption += f"Positioning : [bold]{solar_positioning_algorithm}[/bold], "

                if incidence:
                    incidence_algorithm = get_value_or_default(
                        model_result, INCIDENCE_ALGORITHM_NAME, NOT_AVAILABLE
                    )
                    model_caption += f"Incidence : [bold]{incidence_algorithm}[/bold], "

                shading_algorithm = get_value_or_default(
                    model_result, SHADING_ALGORITHM_NAME, None
                )
                model_caption += f"Shading : [bold]{shading_algorithm}[/bold]"

                # ----------------------------------------------------------------
                model_caption += "\n[underline]Definitions[/underline]  "

                azimuth_origin = get_value_or_default(
                    model_result, AZIMUTH_ORIGIN_NAME, NOT_AVAILABLE
                )
                model_caption += (
                    f"Azimuth origin : [bold green]{azimuth_origin}[/bold green], "
                )

                if incidence:
                    incidence_angle_definition = (
                        get_value_or_default(model_result, INCIDENCE_DEFINITION, None)
                        if incidence
                        else None
                    )
                    model_caption += f"Incidence angle : [bold yellow]{incidence_angle_definition}[/bold yellow]"

                if fingerprint:
                    fingerprint = (
                        get_value_or_default(
                            model_result,
                            FINGERPRINT_COLUMN_NAME,
                            None,
                        )
                        if fingerprint
                        else None
                    )

                # then : Create a Legend table for the symbols in question
                legend = build_legend_table(
                    dictionary=model_result,
                    caption=model_caption,
                    show_header=False,
                    box=None,
                )

                table_obj = Table(
                    *columns,
                    title=title,
                    # caption=model_caption,
                    show_header=True,
                    header_style="bold",
                    row_styles=["none", "dim"],
                    box=SIMPLE_HEAD,
                    highlight=True,
                )

                # -------------------------------------------------- Ugly Hack ---
                if user_requested_timestamps is not None:
                    timestamps = user_requested_timestamps
                # --- Ugly Hack --------------------------------------------------

                for _index, timestamp in enumerate(timestamps):
                    row = []
                    if index:
                        row.append(str(_index + 1))  # count from 1
                    row.append(str(timestamp))

                    # position_parameter_values = {
                    #     SolarPositionParameter.altitude: lambda idx=_index: get_scalar(
                    #         get_section_field_value(model_result, 'Solar Altitude', 'Altitude'),
                    #         idx,
                    #         rounding_places,
                    #     ),
                    position_parameter_values = {
                        SolarPositionParameter.declination: lambda idx=_index: get_scalar(
                            get_section_field_value(
                                model_result,
                                SOLAR_POSITION_PARAMETER_SECTION_NAMES[SolarPositionParameter.declination],
                                SOLAR_POSITION_PARAMETER_COLUMN_NAMES[SolarPositionParameter.declination]
                            ),
                            idx,
                            rounding_places,
                        ),
                        SolarPositionParameter.hour_angle: lambda idx=_index: get_scalar(
                            get_section_field_value(
                                model_result,
                                SOLAR_POSITION_PARAMETER_SECTION_NAMES[SolarPositionParameter.hour_angle],
                                SOLAR_POSITION_PARAMETER_COLUMN_NAMES[SolarPositionParameter.hour_angle]
                            ),
                            idx,
                            rounding_places,
                        ),
                        SolarPositionParameter.zenith: lambda idx=_index: get_scalar(
                            get_section_field_value(
                                model_result,
                                SOLAR_POSITION_PARAMETER_SECTION_NAMES[SolarPositionParameter.zenith],
                                SOLAR_POSITION_PARAMETER_COLUMN_NAMES[SolarPositionParameter.zenith]
                            ),
                            idx,
                            rounding_places,
                        ),
                        SolarPositionParameter.altitude: lambda idx=_index: get_scalar(
                            get_section_field_value(
                                model_result,
                                SOLAR_POSITION_PARAMETER_SECTION_NAMES[SolarPositionParameter.altitude],
                                SOLAR_POSITION_PARAMETER_COLUMN_NAMES[SolarPositionParameter.altitude]
                            ),
                            idx,
                            rounding_places,
                        ),
                        SolarPositionParameter.azimuth: lambda idx=_index: get_scalar(
                            get_section_field_value(
                                model_result,
                                SOLAR_POSITION_PARAMETER_SECTION_NAMES[SolarPositionParameter.azimuth],
                                SOLAR_POSITION_PARAMETER_COLUMN_NAMES[SolarPositionParameter.azimuth]
                            ),
                            idx,
                            rounding_places,
                        ),
                        SolarPositionParameter.incidence: lambda idx=_index: get_scalar(
                            get_section_field_value(
                                model_result,
                                SOLAR_POSITION_PARAMETER_SECTION_NAMES[SolarPositionParameter.incidence],
                                SOLAR_POSITION_PARAMETER_COLUMN_NAMES[SolarPositionParameter.incidence]
                            ),
                            idx,
                            rounding_places,
                        ),
                        SolarPositionParameter.horizon: lambda idx=_index: get_scalar(
                            get_section_field_value(
                                model_result,
                                SOLAR_POSITION_PARAMETER_SECTION_NAMES[SolarPositionParameter.horizon],
                                SOLAR_POSITION_PARAMETER_COLUMN_NAMES[SolarPositionParameter.horizon]
                            ),
                            idx,
                            rounding_places,
                        ),
                        SolarPositionParameter.sun_horizon: lambda idx=_index: get_scalar(
                            get_section_field_value(
                                model_result,
                                SOLAR_POSITION_PARAMETER_SECTION_NAMES[SolarPositionParameter.sun_horizon],
                                SOLAR_POSITION_PARAMETER_COLUMN_NAMES[SolarPositionParameter.sun_horizon]
                            ),
                            idx,
                            rounding_places,
                        ),
                        SolarPositionParameter.visible: lambda idx=_index: get_scalar(
                            get_section_field_value(
                                model_result,
                                SOLAR_POSITION_PARAMETER_SECTION_NAMES[SolarPositionParameter.visible],
                                SOLAR_POSITION_PARAMETER_COLUMN_NAMES[SolarPositionParameter.visible]
                            ),
                            idx,
                            rounding_places,
                        ),
                        SolarPositionParameter.event_type: lambda idx=_index: get_scalar(
                            get_section_field_value(
                                model_result,
                                SOLAR_POSITION_PARAMETER_SECTION_NAMES[SolarPositionParameter.event_type],
                                SOLAR_POSITION_PARAMETER_COLUMN_NAMES[SolarPositionParameter.event_type]
                            ),
                            idx,
                            rounding_places,
                        ),
                        SolarPositionParameter.event_time: lambda idx=_index: get_scalar(
                            get_section_field_value(
                                model_result,
                                SOLAR_POSITION_PARAMETER_SECTION_NAMES[SolarPositionParameter.event_time],
                                SOLAR_POSITION_PARAMETER_COLUMN_NAMES[SolarPositionParameter.event_time]
                            ),
                            idx,
                            rounding_places,
                        ),
                    }
                    # position_parameter_values = {
                    #     SolarPositionParameter.declination: lambda idx=_index: get_scalar(
                    #         get_value_or_default(model_result, SolarPositionParameter.declination),
                    #         idx,
                    #         rounding_places,
                    #     ),
                    #     # SolarPositionParameter.timing: lambda idx=_index: str(get_value_or_default(
                    #     #     model_result, TIME_ALGORITHM_NAME
                    #     # )),
                    #     # SolarPositionParameter.positioning: lambda idx=_index: str(get_value_or_default(
                    #     #     model_result, POSITIONING_ALGORITHM_NAME
                    #     # )),
                    #     SolarPositionParameter.hour_angle: lambda idx=_index: get_scalar(
                    #         get_value_or_default(model_result, SolarPositionParameter.hour_angle),
                    #         idx,
                    #         rounding_places,
                    #     ),
                    #     SolarPositionParameter.zenith: lambda idx=_index: get_scalar(
                    #         get_value_or_default(model_result, SolarPositionParameter.zenith),
                    #         idx,
                    #         rounding_places,
                    #     ),
                    #     SolarPositionParameter.altitude: lambda idx=_index: get_scalar(
                    #         get_value_or_default(model_result, SolarPositionParameter.altitude),
                    #         idx,
                    #         rounding_places,
                    #     ),
                    #     SolarPositionParameter.azimuth: lambda idx=_index: get_scalar(
                    #         get_value_or_default(model_result, SolarPositionParameter.azimuth),
                    #         idx,
                    #         rounding_places,
                    #     ),
                    #     SolarPositionParameter.incidence: lambda idx=_index: get_scalar(
                    #         get_value_or_default(model_result, SolarPositionParameter.incidence),
                    #         idx,
                    #         rounding_places,
                    #     ),
                    #     SolarPositionParameter.horizon: lambda idx=_index: get_scalar(
                    #         get_value_or_default(model_result, SolarPositionParameter.horizon),
                    #         idx,
                    #         rounding_places,
                    #     ),
                    #     SolarPositionParameter.sun_horizon: lambda idx=_index: get_scalar(
                    #         get_value_or_default(model_result, SolarPositionParameter.sun_horizon),
                    #         idx,
                    #         rounding_places,
                    #     ),
                    #     SolarPositionParameter.visible: lambda idx=_index: get_scalar(
                    #         get_value_or_default(model_result, SolarPositionParameter.visible),
                    #         idx,
                    #         rounding_places,
                    #     ),
                    #     SolarPositionParameter.event_type: lambda idx=_index: get_scalar(
                    #         get_value_or_default(
                    #             dictionary=model_result,
                    #             key=SolarPositionParameter.event_type,
                    #             default=None,
                    #         ),
                    #         idx,
                    #         rounding_places,
                    #     ),
                    #     SolarPositionParameter.event_time: lambda idx=_index: get_event_time_value(
                    #             dictionary=model_result,
                    #             idx=idx,
                    #             rounding_places=rounding_places,
                    #     ),
                    # }
                    # print(f"Position Parameter Values :\n\n {position_parameter_values=}\n")

                    # print(f"HERE Model NOW : {model_result=}")
                    for parameter in position_parameters:
                        # print(f"{parameter=}")
                        if parameter in position_parameter_values:
                            # print(f"{position_parameter_values=}")
                            # print(f"{position_parameter_values[parameter]=}")
                            value = position_parameter_values[parameter]()
                            # print(f"{value=}")
                            if value is None:
                                row.append("")
                            elif isinstance(value, tuple):
                                row.extend(str(value))
                            else:
                                from pvgisprototype.api.position.models import SolarEvent
                                from pvgisprototype.api.position.models import SunHorizonPositionModel
                                if isinstance(value, SolarEvent):
                                    row.append(
                                        format_string(value.value, enum_model=SolarEvent)
                                    )
                                elif value == SunHorizonPositionModel.above.value:
                                    yellow_value = Text(
                                        str(round_float_values(value, rounding_places)),
                                        style="bold yellow",
                                    )
                                    row.append(yellow_value)
                                elif value == SunHorizonPositionModel.low_angle.value:
                                    orange_value = Text(
                                        str(round_float_values(value, rounding_places)),
                                        style="dark_orange",
                                    )
                                    row.append(orange_value)
                                elif value == SunHorizonPositionModel.below.value:
                                    red_value = Text(
                                        str(round_float_values(value, rounding_places)),
                                        style="red",
                                    )
                                    row.append(red_value)
                                elif isinstance(value, datetime64):
                                    if isna(value):  # Check for NaT
                                        row.append("")
                                    else:
                                        # Convert to Python datetime
                                        dt = value.astype('datetime64[s]').astype('O')
                                        # Extract time
                                        row.append(str(dt.time()))
                                else:  # value is not None:
                                    if value < 0:  # Avoid matching any `-`
                                        # Make them bold red
                                        red_value = Text(
                                            str(round_float_values(value, rounding_places)),
                                            style="bold red",
                                        )
                                        row.append(red_value)
                                    else:
                                        row.append(str(value))
                            
                    table_obj.add_row(*row)

                # # Build the sparkline
                # from pvgisprototype.cli.print.sparklines import convert_series_to_sparkline

                # sparkline = (
                #     convert_series_to_sparkline(series, timestamps, frequency)
                #     if series.size > 0
                #     else ""
                # )
                # if sparkline:
                #     row.extend([sparkline])

                console.print(table_obj)
                # Create Panels for time, caption and legend
                time_table = build_time_table()
                frequency, frequency_label = infer_frequency_from_timestamps(timestamps)
                time_table.add_row(
                    str(timestamps.strftime("%Y-%m-%d %H:%M").values[0]),
                    str(frequency) if frequency and frequency != 'Single' else '-',
                    str(timestamps.strftime("%Y-%m-%d %H:%M").values[-1]),
                    str(timezone),
                )
                time_panel = build_time_panel(time_table, padding=(0, 1, 0, 1))
                caption_panel = Panel(
                    model_caption,
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
                version_and_fingerprint_and_column = build_version_and_fingerprint_columns(
                    version=version,
                    fingerprint=fingerprint,
                )
                # Use Columns to place them side-by-side
                from rich.columns import Columns
                console.print(Columns([
                        time_panel,
                        caption_panel,
                        legend_panel,
                    ]))
                console.print( version_and_fingerprint_and_column)
           

def print_solar_position_series_in_columns(
    longitude,
    latitude,
    timestamps,
    timezone,
    table,
    rounding_places=ROUNDING_PLACES_DEFAULT,
    index: bool = False,
):
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
