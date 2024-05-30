from pandas import to_datetime
from datetime import datetime

from typer.main import solve_typer_info_defaults
from pvgisprototype.api.position.models import SOLAR_POSITION_PARAMETER_COLUMN_NAMES, SolarPositionParameter
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import round_float_values
from rich.console import Console
from rich.table import Table
from rich.columns import Columns
from rich.panel import Panel
from rich.pretty import Pretty
from rich.text import Text
from rich.box import SIMPLE, SIMPLE_HEAD, SIMPLE_HEAVY, ROUNDED, HORIZONTALS
from typing import List, Sequence
import numpy as np
from pvgisprototype.constants import (
    TITLE_KEY_NAME,
    LONGITUDE_COLUMN_NAME,
    LATITUDE_COLUMN_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_NAME,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_NAME,
    POWER_MODEL_COLUMN_NAME,
    RADIATION_MODEL_COLUMN_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    TIME_ALGORITHM_NAME,
    SOLAR_TIME_COLUMN_NAME,
    DECLINATION_COLUMN_NAME,
    DECLINATION_NAME,
    HOUR_ANGLE_COLUMN_NAME,
    HOUR_ANGLE_NAME,
    POSITIONING_ALGORITHM_COLUMN_NAME,
    POSITIONING_ALGORITHM_NAME,
    SOLAR_CONSTANT_COLUMN_NAME,
    PERIGEE_OFFSET_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
    ZENITH_COLUMN_NAME,
    ZENITH_NAME,
    ALTITUDE_COLUMN_NAME,
    ALTITUDE_NAME,
    AZIMUTH_COLUMN_NAME,
    AZIMUTH_NAME,
    AZIMUTH_ORIGIN_COLUMN_NAME,
    AZIMUTH_ORIGIN_NAME,
    INCIDENCE_ALGORITHM_COLUMN_NAME,
    INCIDENCE_ALGORITHM_NAME,
    INCIDENCE_COLUMN_NAME,
    INCIDENCE_NAME,
    INCIDENCE_DEFINITION,
    UNITS_COLUMN_NAME,
    UNITLESS,
    UNITS_NAME,
    ANGLE_UNITS_NAME,
    ANGLE_UNITS_COLUMN_NAME,
    NOT_AVAILABLE,
    ROUNDING_PLACES_DEFAULT,
    RADIANS,
    FINGERPRINT_NAME,
    FINGERPRINT_COLUMN_NAME,
)


def style_value(value, style_if_negative='dim'):
    if value is not None:
        if value < 0:
            return f"[{style_if_negative}]{value}[/]"
        else:
            return str(value)
    return None


def get_scalar(value, index, places):
    """Safely get a scalar value from an array or return the value itself """
    if isinstance(value, np.ndarray):
        if value.size > 1:
            return value[index]
        else: 
            return value[0]

    return value


def get_value_or_default(dictionary, key, default=NOT_AVAILABLE):
    """Get a value from a dictionary or return a default value"""
    return dictionary.get(key, default)


def safe_get_value(dictionary, key, index, default=NOT_AVAILABLE):
    """
    Parameters
    ----------
    dictionary: dict
        Input dictionary
    key: str
        key to retrieve from the dictionary
    index: int
        index ... ?

    Returns
    -------
    The value corresponding to the given `key` in the `dictionary` or the
    default value if the key does not exist.

    """
    value = dictionary.get(key, default)
    # if isinstance(value, np.ndarray) and value.size > 1:
    if isinstance(value, (list, np.ndarray)) and len(value) > index:
        return value[index]
    return value


def print_table(headers: List[str], data: List[List[str]]) -> None:
    """Create and print a table with provided headers and data."""
    table = Table(show_header=True, header_style="bold magenta", box=SIMPLE_HEAD)
    for header in headers:
        table.add_column(header)

    for row_data in data:
        table.add_row(*row_data)

    Console().print(table)


def build_caption(
    longitude, latitude, rounded_table, timezone, user_requested_timezone
):
    first_model = next(iter(rounded_table))
    caption = (
        f"[underline]Position[/underline]  "
        f"{LONGITUDE_COLUMN_NAME}, {LATITUDE_COLUMN_NAME} = [bold]{longitude}[/bold], [bold]{latitude}[/bold], "
        f"Orientation : [bold blue]{rounded_table[first_model].get(SURFACE_ORIENTATION_NAME, None)}[/bold blue], "
        f"Tilt : [bold blue]{rounded_table[first_model].get(SURFACE_TILT_NAME, None)}[/bold blue] "
        f"[[dim]{rounded_table[first_model].get(UNITS_NAME, UNITLESS)}[/dim]]"

        f"\n[underline]Algorithms[/underline]  " # ---------------------------
        f"Timing : [bold]{rounded_table[first_model].get(TIME_ALGORITHM_NAME, NOT_AVAILABLE)}[/bold], "
        f"Zone : {timezone}, "
        f"Local zone : {user_requested_timezone if user_requested_timezone else 'N/A'}, "

        # f"Positioning: {rounded_table[first_model].get(POSITIONING_ALGORITHM_NAME, NOT_AVAILABLE)}, "
        # f"Incidence: {rounded_table[first_model].get(INCIDENCE_ALGORITHM_NAME, NOT_AVAILABLE)}\n"
        
        # f"[underline]Definitions[/underline]  "
        # f"Azimuth origin: {rounded_table[first_model].get(AZIMUTH_ORIGIN_NAME, NOT_AVAILABLE)}, "
        # f"Incidence angle: {rounded_table[first_model].get(INCIDENCE_DEFINITION, NOT_AVAILABLE)}\n"
    )
    return caption


def print_solar_position_table_panels(
    longitude,
    latitude,
    timestamp,
    timezone,
    solar_position_table,
    rounding_places = ROUNDING_PLACES_DEFAULT,
    position_parameters = SolarPositionParameter.all,
    surface_orientation = True,
    surface_tilt = True,
    user_requested_timestamp = None,
    user_requested_timezone = None,
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
    latitude = round_float_values(latitude, rounding_places)
    longest_label_length = max(len(key) for key in first_model.keys())
    surface_position_keys = {
            SURFACE_ORIENTATION_NAME,
            SURFACE_TILT_NAME,
            ANGLE_UNITS_NAME,
            INCIDENCE_DEFINITION,
            UNITS_NAME,
            }
    for key, value in first_model.items():
        if key in surface_position_keys:
            padded_key = f"{key} :".ljust(longest_label_length + 3, ' ')
            if key == INCIDENCE_DEFINITION:
                value = f"[yellow]{value}[/yellow]"
            table.add_row(padded_key, str(value))
    position_panel = Panel(
            table,
            title="Surface Position",
            box=HORIZONTALS,
            style='',
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
                get_value_or_default(model_result, DECLINATION_NAME), idx, rounding_places
            ),
            # SolarPositionParameter.timing: lambda idx=_index: str(get_value_or_default(
            #     model_result, TIME_ALGORITHM_NAME
            # )),
            # SolarPositionParameter.positioning: lambda idx=_index: str(get_value_or_default(
            #     model_result, POSITIONING_ALGORITHM_NAME
            # )),
            SolarPositionParameter.hour_angle: lambda idx=_index: get_scalar(
                get_value_or_default(model_result, HOUR_ANGLE_NAME), idx, rounding_places
            ),
            SolarPositionParameter.zenith: lambda idx=_index: get_scalar(
                get_value_or_default(model_result, ZENITH_NAME), idx, rounding_places
            ),
            SolarPositionParameter.altitude: lambda idx=_index: get_scalar(
                get_value_or_default(model_result, ALTITUDE_NAME), idx, rounding_places
            ),
            SolarPositionParameter.azimuth: lambda idx=_index: get_scalar(
                get_value_or_default(model_result, AZIMUTH_NAME), idx, rounding_places
            ),
            SolarPositionParameter.incidence: lambda idx=_index: get_scalar(get_value_or_default(model_result, INCIDENCE_NAME), idx, rounding_places,
            ),
        }
        for parameter in position_parameters:
            if parameter in position_parameter_values:
                padded_key = f"{parameter.value} :".ljust(longest_label_length + 1, ' ')
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
    Console().print(columns)


def print_solar_position_series_table(
    longitude,
    latitude,
    timestamps,
    timezone,
    table,
    position_parameters: Sequence[SolarPositionParameter] = SolarPositionParameter.all,
    title='Solar position overview',
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
            from pvgisprototype.cli.print import print_solar_position_table_panels
            print_solar_position_table_panels(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamps,
                timezone=timezone,
                solar_position_table=rounded_table,
                position_parameters=position_parameters,
                rounding_places=rounding_places,
                user_requested_timestamp=user_requested_timestamps, 
                user_requested_timezone=user_requested_timezone
            )
    else:
        longitude = round_float_values(longitude, rounding_places)
        latitude = round_float_values(latitude, rounding_places)


        columns = []
        if index:
            columns.append("Index")
        if timestamps is not None:
            columns.append('Time')

        for parameter in position_parameters:
            if parameter in SOLAR_POSITION_PARAMETER_COLUMN_NAMES:
                column = SOLAR_POSITION_PARAMETER_COLUMN_NAMES[parameter]
                if isinstance(column, list):
                    columns.extend(column)
                else:
                    columns.append(column)

        caption = build_caption(
            longitude, latitude, rounded_table, timezone, user_requested_timezone
        )

        for _, model_result in rounded_table.items():
            model_caption = caption
            
            position_algorithm = get_value_or_default(model_result, POSITIONING_ALGORITHM_NAME, NOT_AVAILABLE)
            model_caption += f"Positioning : [bold]{position_algorithm}[/bold], "
            
            incidence_algorithm = get_value_or_default(model_result, INCIDENCE_ALGORITHM_NAME, NOT_AVAILABLE)
            model_caption += f"Incidence : [bold]{incidence_algorithm}[/bold], "
            
            model_caption += f"\n[underline]Definitions[/underline]  " # -----------

            azimuth_origin = get_value_or_default(model_result, AZIMUTH_ORIGIN_NAME, NOT_AVAILABLE)
            model_caption += f"Azimuth origin : [bold green]{azimuth_origin}[/bold green], "
            
            incidence_angle_definition = get_value_or_default(model_result, INCIDENCE_DEFINITION, None) if incidence else None
            model_caption += f"Incidence angle : [bold yellow]{incidence_angle_definition}[/bold yellow]"

            table_obj = Table(
                *columns,
                title=title,
                caption=model_caption,
                box=SIMPLE_HEAD,
            )

            for _index, timestamp in enumerate(timestamps):
                row = []
                if index:
                    row.append(str(_index + 1))  # count from 1
                row.append(str(timestamp))

                position_parameter_values = {
                    SolarPositionParameter.declination: lambda idx=_index: get_scalar(
                        get_value_or_default(model_result, DECLINATION_NAME), idx, rounding_places
                    ),
                    # SolarPositionParameter.timing: lambda idx=_index: str(get_value_or_default(
                    #     model_result, TIME_ALGORITHM_NAME
                    # )),
                    # SolarPositionParameter.positioning: lambda idx=_index: str(get_value_or_default(
                    #     model_result, POSITIONING_ALGORITHM_NAME
                    # )),
                    SolarPositionParameter.hour_angle: lambda idx=_index: get_scalar(
                        get_value_or_default(model_result, HOUR_ANGLE_NAME), idx, rounding_places
                    ),
                    SolarPositionParameter.zenith: lambda idx=_index: get_scalar(
                        get_value_or_default(model_result, ZENITH_NAME), idx, rounding_places
                    ),
                    SolarPositionParameter.altitude: lambda idx=_index: get_scalar(
                        get_value_or_default(model_result, ALTITUDE_NAME), idx, rounding_places
                    ),
                    SolarPositionParameter.azimuth: lambda idx=_index: get_scalar(
                        get_value_or_default(model_result, AZIMUTH_NAME), idx, rounding_places
                    ),
                    SolarPositionParameter.incidence: lambda idx=_index: get_scalar(get_value_or_default(model_result, INCIDENCE_NAME), idx, rounding_places,
                    ),
                }

                for parameter in position_parameters:
                    if parameter in position_parameter_values:
                        value = position_parameter_values[parameter]()
                        if isinstance(value, tuple):
                            row.extend(str(value))
                        else:
                            row.append(str(value))

                table_obj.add_row(*row)

            Console().print(table_obj)


def print_hour_angle_table_2(
    solar_time,
    rounding_places,
    hour_angle=None,
    units=None,
) -> None:
    """ """
    solar_time = round_float_values(solar_time, rounding_places)
    hour_angle = round_float_values(hour_angle, rounding_places)

    columns = [SOLAR_TIME_COLUMN_NAME]
    if hour_angle is not None:
        columns.append(HOUR_ANGLE_COLUMN_NAME)
    columns.append(UNITS_COLUMN_NAME)

    table = Table(
        *columns,
        box=SIMPLE_HEAD,
        show_header=True,
        header_style="bold magenta",
    )

    row = [str(solar_time)]
    if hour_angle is not None:
        row.append(str(hour_angle))
    row.append(str(units))
    table.add_row(*row)

    Console().print(table)


def print_hour_angle_table(
    latitude,
    rounding_places,
    surface_tilt=None,
    declination=None,
    hour_angle=None,
    units=None,
) -> None:
    """ """
    latitude = round_float_values(latitude, rounding_places)
    # rounded_table = round_float_values(table, rounding_places)
    surface_tilt = round_float_values(surface_tilt, rounding_places)
    declination = round_float_values(declination, rounding_places)
    hour_angle = round_float_values(hour_angle, rounding_places)

    columns = ["Latitude", "Event"]
    if surface_tilt is not None:
        columns.append(SURFACE_TILT_COLUMN_NAME)
    if declination is not None:
        columns.append(DECLINATION_COLUMN_NAME)
    if hour_angle is not None:
        columns.append(HOUR_ANGLE_COLUMN_NAME)
    columns.append(UNITS_COLUMN_NAME)

    table = Table(
        *columns,
        box=SIMPLE_HEAD,
        show_header=True,
        header_style="bold magenta",
    )

    row = [str(latitude), 'Event']
    if surface_tilt is not None:
        row.append(str(surface_tilt))
    if declination is not None:
        row.append(str(declination))
    if hour_angle is not None:
        row.append(str(hour_angle))
    row.append(str(units))
    table.add_row(*row)

    Console().print(table)


def print_quantity_table(
    dictionary: dict = dict(),
    title: str ='Series',
    main_key: str = None,
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    verbose=1,
    index: bool = False,
) -> None:
    table = Table(title=title, box=SIMPLE_HEAD)
    
    if index:
        table.add_column("Index")

    # remove the 'Title' entry! ---------------------------------------------
    dictionary.pop(TITLE_KEY_NAME, NOT_AVAILABLE)
    # ------------------------------------------------------------- Important

    # # base columns
    # if verbose > 0:

    # additional columns based dictionary keys
    for key in dictionary.keys():
        if dictionary[key] is not None:
            table.add_column(key)
    
    if not main_key:  # consider the 1st key of having the "valid" number of values
        main_key = list(dictionary.keys())[0]

    # Convert single float or int values to arrays of the same length as the "main' key
    for key, value in dictionary.items():
        if isinstance(value, (float, int)):
            dictionary[key] = np.full(len(dictionary[main_key]), value)

        if isinstance(value, str):
            dictionary[key] = np.full(len(dictionary[main_key]), str(value))
    
    # Zip series
    zipped_series = zip(*dictionary.values())

    # Populate table
    index_counter = 1
    for values in zipped_series:
        row = []

        if index:
            row.append(str(index_counter))
            index_counter += 1

        for idx, (column_name, value) in enumerate(zip(dictionary.keys(), values)):
            if idx == 0:  # assuming after 'Time' is the value of main interest
                bold_value = Text(str(round_float_values(value, rounding_places)), style="bold")
                row.append(bold_value)
            else:
                if not isinstance(value, str):
                    if column_name == 'Loss':
                        red_value = Text(str(round_float_values(value, rounding_places)), style="bold red")
                        row.append(red_value)
                    else:
                        row.append(str(round_float_values(value, rounding_places)))
                else:
                    row.append(value)
        table.add_row(*row)

    if verbose:
        Console().print(table)


def print_irradiance_table_2(
    longitude=None,
    latitude=None,
    elevation=None,
    timestamps: datetime = [datetime.now()],
    dictionary: dict = dict(),
    title: str ='Irradiance series',
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    verbose=1,
    index: bool = False,
    surface_orientation=True,
    surface_tilt=True,
) -> None:
    """
    """
    longitude = round_float_values(longitude, rounding_places)
    latitude = round_float_values(latitude, rounding_places)
    elevation = round_float_values(elevation, 0)#rounding_places)
    rounded_table = round_float_values(dictionary, rounding_places)

    caption = str()
    if longitude or latitude or elevation:
        caption = f"[underline]Position[/underline]  "
    if longitude and latitude:
        caption += f"{LONGITUDE_COLUMN_NAME}, {LATITUDE_COLUMN_NAME} = [bold]{longitude}[/bold], [bold]{latitude}[/bold], "
    if elevation:
        caption += f"Elevation: [bold]{elevation} m[/bold]"

    surface_orientation = dictionary.get(SURFACE_ORIENTATION_COLUMN_NAME, None) if surface_orientation else None
    surface_tilt = dictionary.get(SURFACE_TILT_COLUMN_NAME, None) if surface_tilt else None
    if surface_orientation or surface_tilt:
        caption += f"\n[underline]Solar surface[/underline]  "

    if surface_orientation is not None:
        caption += f"{SURFACE_ORIENTATION_COLUMN_NAME}: [bold]{surface_orientation}[/bold], "

    if surface_tilt is not None:
        caption += f"{SURFACE_TILT_COLUMN_NAME}: [bold]{surface_tilt}[/bold] "

    units = dictionary.get(ANGLE_UNITS_COLUMN_NAME, UNITLESS)
    if longitude or latitude or elevation or surface_orientation or surface_tilt and units is not None:
        caption += f"[[dim]{units}[/dim]]"
    
    algorithms = dictionary.get(POWER_MODEL_COLUMN_NAME, None)
    radiation_model = dictionary.get(RADIATION_MODEL_COLUMN_NAME, None)
    timing_algorithm = dictionary.get(TIME_ALGORITHM_COLUMN_NAME, NOT_AVAILABLE)  # If timing is a single value and not a list
    position_algorithm = dictionary.get(POSITIONING_ALGORITHM_COLUMN_NAME, NOT_AVAILABLE)
    azimuth_origin = dictionary.get(AZIMUTH_ORIGIN_COLUMN_NAME, NOT_AVAILABLE)
    incidence_algorithm = dictionary.get(INCIDENCE_ALGORITHM_COLUMN_NAME, NOT_AVAILABLE)

    if algorithms or radiation_model or timing_algorithm or position_algorithm:
        caption += f"\n[underline]Algorithms[/underline]  "

    if algorithms:
        caption += f"{POWER_MODEL_COLUMN_NAME}: [bold]{algorithms}[/bold], "

    if radiation_model:
        caption += f"{RADIATION_MODEL_COLUMN_NAME}: [bold]{radiation_model}[/bold], "

    if timing_algorithm:
        caption += f"Timing : [bold]{timing_algorithm}[/bold], "

    if position_algorithm:
        caption += f"Positioning : [bold]{position_algorithm}[/bold], "

    if azimuth_origin:
        caption += f"Azimuth origin : [bold indigo]{azimuth_origin}[/bold indigo]"

    if incidence_algorithm:
        caption += f"Incidence : [bold yellow]{incidence_algorithm}[/bold yellow], "

    # solar_incidence_algorithm = dictionary.get(INCIDENCE_ALGORITHM_COLUMN_NAME, None)
    # if solar_incidence_algorithm is not None:
    #     caption += f"{INCIDENCE_ALGORITHM_COLUMN_NAME}: [bold yellow]{solar_incidence_algorithm}[/bold yellow], "

    solar_incidence_definition = dictionary.get(INCIDENCE_DEFINITION, None)
    if solar_incidence_definition is not None:
        caption += f"{INCIDENCE_DEFINITION}: [bold yellow]{solar_incidence_definition}[/bold yellow]"

    solar_constant = dictionary.get(SOLAR_CONSTANT_COLUMN_NAME, None)
    perigee_offset = dictionary.get(PERIGEE_OFFSET_COLUMN_NAME, None)
    eccentricity_correction_factor = dictionary.get(ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME, None)

    if solar_constant and perigee_offset and eccentricity_correction_factor:
        caption += f'\n[underline]Constants[/underline] '
        caption += f'{SOLAR_CONSTANT_COLUMN_NAME} : {solar_constant}, '
        caption += f'{PERIGEE_OFFSET_COLUMN_NAME} : {perigee_offset}, '
        caption += f'{ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME} : {eccentricity_correction_factor}, '

    from pvgisprototype.constants import SYMBOL_DESCRIPTIONS
    # add a caption for symbols found in the input dictionary
    caption += '\n[underline]Legend[/underline] '
    for symbol, description in SYMBOL_DESCRIPTIONS.items():
        if any(symbol in key for key in dictionary.keys()):
            caption += f"[yellow]{symbol}[/yellow] is {description}, "
    caption=caption.rstrip(', ')  # Remove trailing comma + space

    table = Table(
            title=title,
            caption=caption.rstrip(', '),  # Remove trailing comma + space
            caption_justify="center",
            expand=False,
            padding=(0, 2),
            box=SIMPLE_HEAD,
            show_footer=True,
            )
    
    if index:
        table.add_column("Index")

    # base columns
    table.add_column('Time')  # footer = 'Something'
    
    # remove the 'Title' entry! ---------------------------------------------
    dictionary.pop('Title', NOT_AVAILABLE)
    # ------------------------------------------------------------- Important

    keys_to_exclude = {
            SURFACE_ORIENTATION_COLUMN_NAME,
            SURFACE_TILT_COLUMN_NAME,
            ANGLE_UNITS_COLUMN_NAME,
            TIME_ALGORITHM_COLUMN_NAME,
            POSITIONING_ALGORITHM_COLUMN_NAME,
            INCIDENCE_ALGORITHM_COLUMN_NAME,
            INCIDENCE_DEFINITION,
            RADIATION_MODEL_COLUMN_NAME,
            POWER_MODEL_COLUMN_NAME,
            FINGERPRINT_COLUMN_NAME,
            SOLAR_CONSTANT_COLUMN_NAME,
            PERIGEE_OFFSET_COLUMN_NAME,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
    }

    # add and process additional columns
    for key, value in dictionary.items():
        if key not in keys_to_exclude:

            if isinstance(value, np.ndarray) and value.dtype.kind in "if":
                sum_of_key_value = str(value.sum())

            if isinstance(value, (float, int)):
                dictionary[key] = np.full(len(timestamps), value)

            if isinstance(value, str):
                dictionary[key] = np.full(len(timestamps), str(value))

            if sum_of_key_value:
                table.add_column(key, footer=sum_of_key_value)
            else:
                table.add_column(key)


            # if dictionary[key] is not None and key_sum:

            # if dictionary[key] is not None:

    
    # Zip series and timestamps
    filtered_dictionary = {key: value for key, value in dictionary.items() if key not in keys_to_exclude}
    zipped_series = zip(*filtered_dictionary.values())
    zipped_data = zip(timestamps, zipped_series)

    # Populate table
    index_counter = 1
    for timestamp, values in zipped_data:
        row = []

        if index:
            row.append(str(index_counter))
            index_counter += 1

        row.append(to_datetime(timestamp).strftime('%Y-%m-%d %H:%M:%S'))

        for idx, (column_name, value) in enumerate(zip(filtered_dictionary.keys(), values)):
            if idx == 0:  # assuming after 'Time' is the value of main interest
                bold_value = Text(str(round_float_values(value, rounding_places)), style="bold")
                row.append(bold_value)
            else:
                if not isinstance(value, str):
                    if column_name == 'Loss':
                        red_value = Text(str(round_float_values(value, rounding_places)), style="bold red")
                        row.append(red_value)
                    else:
                        row.append(str(round_float_values(value, rounding_places)))
                else:
                    if value is not None:
                        row.append(value)
        table.add_row(*row)

    if verbose:
        Console().print(table)


def print_finger_hash(dictionary: dict):
    """ """
    fingerprint = dictionary.get(FINGERPRINT_COLUMN_NAME, None)
    if fingerprint is not None:
        fingerprint_panel = Panel.fit(
            Text(f"{fingerprint}", justify="center", style="bold yellow"),
            subtitle="[reverse]Fingerprint[/reverse]",
            subtitle_align="right",
            border_style="dim",
            style="dim",
        )
        Console().print(fingerprint_panel)


from click import Context
def print_command_metadata(context: Context):
    """
    """
    command_parameters = {}
    command_parameters['command'] = context.command_path
    command_parameters = command_parameters | context.params
    command_parameters_panel = Panel.fit(
        Pretty(command_parameters, no_wrap=True),
        subtitle="[reverse]Command Metadata[/reverse]",
        subtitle_align="right",
        border_style="dim",
        style="dim",
    )
    Console().print(command_parameters_panel)

    # write to file ?
    import json
    from pvgisprototype.validation.serialisation import CustomEncoder
    with open('command_parameters.json', 'w') as json_file:
        json.dump(command_parameters, json_file, cls=CustomEncoder, indent=4)


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
        parameters = ["Declination", "Hour Angle", "Zenith", "Altitude", "Azimuth", "Incidence"]
        for param in parameters:
            # Assume `table` is a dictionary of models, each containing a list of values for each parameter
            values = [round_float_values(model_result[param][i], rounding_places) for model_name, model_result in table.items() if param in model_result]
            value_str = ", ".join(map(str, values))  # Combine values from all models
            table_panel.add_row(param, value_str)

        panel = Panel(table_panel, expand=True)
        panels.append(panel)

    Console().print(Columns(panels))
