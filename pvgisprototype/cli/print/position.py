from pvgisprototype.cli.print.helpers import get_value_or_default
from pvgisprototype.cli.print.helpers import build_caption
from typing import Sequence
from numpy import ndarray
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich.columns import Columns
from rich.box import HORIZONTALS, ROUNDED, SIMPLE_HEAD
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
    SUN_HORIZON_NAME,
    SURFACE_ORIENTATION_NAME,
    SURFACE_TILT_NAME,
    TIME_COLUMN_NAME,
    UNIT_NAME,
    VISIBLE_COLUMN_NAME,
    ZENITH_COLUMN_NAME,
)

console = Console()


def get_scalar(value, index, places):
    """Safely get a scalar value from an array or return the value itself"""
    if isinstance(value, ndarray):
        if value.size > 1:
            return value[index]
        else:
            return value[0]

    return value


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
                                     ALTITUDE_COLUMN_NAME), idx, rounding_places
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
    surface_orientation=None,
    surface_tilt=None,
    incidence=None,
    user_requested_timestamps=None,
    user_requested_timezone=None,
    rounding_places=ROUNDING_PLACES_DEFAULT,
    group_models=False,
    panels=False,
) -> None:
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

        for parameter in position_parameters:
            if parameter in SOLAR_POSITION_PARAMETER_COLUMN_NAMES:
                column = SOLAR_POSITION_PARAMETER_COLUMN_NAMES[parameter]
                if isinstance(column, list):
                    columns.extend(column)
                else:
                    columns.append(column)


        # Caption

        ## Position

        caption = build_caption(
            longitude, latitude, rounded_table, timezone, user_requested_timezone
        )

        for _, model_result in rounded_table.items():
            model_caption = caption

            position_algorithm = get_value_or_default(
                model_result, POSITIONING_ALGORITHM_NAME, NOT_AVAILABLE
            )
            model_caption += f"Positioning : [bold]{position_algorithm}[/bold], "

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

                position_parameter_values = {
                    SolarPositionParameter.declination: lambda idx=_index: get_scalar(
                        get_value_or_default(model_result, SolarPositionParameter.declination),
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
                        get_value_or_default(model_result, SolarPositionParameter.hour_angle),
                        idx,
                        rounding_places,
                    ),
                    SolarPositionParameter.zenith: lambda idx=_index: get_scalar(
                        get_value_or_default(model_result, SolarPositionParameter.zenith),
                        idx,
                        rounding_places,
                    ),
                    SolarPositionParameter.altitude: lambda idx=_index: get_scalar(
                        get_value_or_default(model_result, SolarPositionParameter.altitude),
                        idx,
                        rounding_places,
                    ),
                    SolarPositionParameter.azimuth: lambda idx=_index: get_scalar(
                        get_value_or_default(model_result, SolarPositionParameter.azimuth),
                        idx,
                        rounding_places,
                    ),
                    SolarPositionParameter.incidence: lambda idx=_index: get_scalar(
                        get_value_or_default(model_result, SolarPositionParameter.incidence),
                        idx,
                        rounding_places,
                    ),
                    SolarPositionParameter.horizon: lambda idx=_index: get_scalar(
                        get_value_or_default(model_result, HORIZON_HEIGHT_COLUMN_NAME),
                        idx,
                        rounding_places,
                    ),
                    # SolarPositionParameter.behind_horizon: lambda idx=_index: get_scalar(
                    #     get_value_or_default(model_result, BEHIND_HORIZON_NAME),
                    #     idx,
                    #     rounding_places,
                    # ),
                    SolarPositionParameter.sun_horizon: lambda idx=_index: get_scalar(
                        get_value_or_default(model_result, SolarPositionParameter.sun_horizon),
                        idx,
                        rounding_places,
                    ),
                    SolarPositionParameter.visible: lambda idx=_index: get_scalar(
                        get_value_or_default(model_result, VISIBLE_COLUMN_NAME),
                        idx,
                        rounding_places,
                    ),
                }

                for parameter in position_parameters:
                    if parameter in position_parameter_values:
                        value = position_parameter_values[parameter]()
                        if isinstance(value, tuple):
                            row.extend(str(value))
                        else:
                            from pvgisprototype.api.position.models import SunHorizonPositionModel
                            from rich.text import Text
                            if value == SunHorizonPositionModel.above.value:
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
                            else:  # value is not None:
                                row.append(str(value))

                table_obj.add_row(*row)

            console.print(table_obj)
            # console.print(Panel(model_caption, expand=False))
            # Create Panels for both caption and legend
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
            # Use Columns to place them side-by-side
            from rich.columns import Columns
            Console().print(Columns([caption_panel, legend_panel]))


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
