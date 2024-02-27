from pandas import to_datetime
from datetime import datetime
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import round_float_values
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import List
import numpy as np
from pvgisprototype.constants import (
    TITLE_KEY_NAME,
    LONGITUDE_COLUMN_NAME,
    LATITUDE_COLUMN_NAME,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_NAME,
    TIME_ALGORITHM_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    SOLAR_TIME_COLUMN_NAME,
    DECLINATION_COLUMN_NAME,
    DECLINATION_NAME,
    HOUR_ANGLE_COLUMN_NAME,
    HOUR_ANGLE_NAME,
    POSITION_ALGORITHM_COLUMN_NAME,
    POSITION_ALGORITHM_NAME,
    ZENITH_COLUMN_NAME,
    ZENITH_NAME,
    ALTITUDE_COLUMN_NAME,
    ALTITUDE_NAME,
    AZIMUTH_COLUMN_NAME,
    AZIMUTH_NAME,
    INCIDENCE_COLUMN_NAME,
    INCIDENCE_NAME,
    INCIDENCE_DEFINITION,
    UNITS_COLUMN_NAME,
    UNITLESS,
    UNITS_NAME,
    NOT_AVAILABLE,
    ROUNDING_PLACES_DEFAULT,
    RADIANS,
)


def safe_get_value(dictionary, key, index, default='NA'):
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
    if isinstance(value, (list, np.ndarray)) and len(value) > index:
        return value[index]
    return value


def print_table(headers: List[str], data: List[List[str]]):
    """Create and print a table with provided headers and data."""
    table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE_HEAD)
    for header in headers:
        table.add_column(header)

    for row_data in data:
        table.add_row(*row_data)

    console = Console()
    console.print(table)


def print_solar_position_table(
    longitude,
    latitude,
    timestamp,
    timezone,
    table,
    declination=None,
    hour_angle=None,
    timing=None,
    zenith=None,
    altitude=None,
    azimuth=None,
    incidence=None,
    user_requested_timestamp=None,
    user_requested_timezone=None,
    rounding_places=ROUNDING_PLACES_DEFAULT,
):
    """
    """
    longitude = round_float_values(longitude, rounding_places)
    latitude = round_float_values(latitude, rounding_places)
    rounded_table = round_float_values(table, rounding_places)
    quantities = [declination, zenith, altitude, azimuth, incidence]

    columns = []
    if longitude is not None:
        columns.append(LONGITUDE_COLUMN_NAME)
    if latitude is not None:
        columns.append(LATITUDE_COLUMN_NAME)
    if timestamp is not None:
        columns.append('Time')
    if timezone is not None:
        columns.append('Zone')
    if user_requested_timestamp and user_requested_timezone:
        columns.extend(["Local Time", "Local Zone"])
    if timing is not None:
        columns.append(TIME_ALGORITHM_COLUMN_NAME)
    if declination is not None:
        columns.append(DECLINATION_COLUMN_NAME)
    if hour_angle is not None:
        columns.append(HOUR_ANGLE_COLUMN_NAME)
    if any(quantity is not None for quantity in quantities):
        columns.append(POSITION_ALGORITHM_COLUMN_NAME)
    if zenith is not None:
        columns.append(ZENITH_COLUMN_NAME)
    if altitude is not None:
        columns.append(ALTITUDE_COLUMN_NAME)
    if azimuth is not None:
        columns.append(AZIMUTH_COLUMN_NAME)
    if incidence is not None:
        columns.append(INCIDENCE_COLUMN_NAME)
    columns.append(UNITS_COLUMN_NAME)

    table = Table(*columns, box=box.SIMPLE_HEAD)

    get_value_or_default = (
        lambda dictionary, key, default="-", not_available=NOT_AVAILABLE: default
        if dictionary.get(key, not_available) is None
        else dictionary.get(key, not_available)
    )

    for model_result in rounded_table:
        declination_value = get_value_or_default(model_result, DECLINATION_NAME)
        hour_angle_value = get_value_or_default(model_result, HOUR_ANGLE_NAME)
        timing_algorithm = get_value_or_default(model_result, TIME_ALGORITHM_NAME)
        position_algorithm = get_value_or_default(model_result, POSITION_ALGORITHM_NAME)
        zenith_value = get_value_or_default(model_result, ZENITH_NAME)
        altitude_value = get_value_or_default(model_result, ALTITUDE_NAME)
        azimuth_value = get_value_or_default(model_result, AZIMUTH_NAME)
        incidence_value = get_value_or_default(model_result, INCIDENCE_NAME)
        units = model_result.get(UNITS_NAME, UNITLESS)

        row = []
        if longitude:
            row.append(str(longitude))
        if latitude:
            row.append(str(latitude))
        row.extend([str(timestamp), str(timezone)])

       # ---------------------------------------------------- Implement-Me---
       # Convert the result back to the user's time zone
       # output_timestamp = output_timestamp.astimezone(user_timezone)
       # --------------------------------------------------------------------

       # Redesign Me! =======================================================
        if user_requested_timestamp and user_requested_timezone:
            row.extend([str(user_requested_timestamp), str(user_requested_timezone)])
       #=====================================================================

        if timing is not None:
            row.append(timing_algorithm)
        if declination_value is not NOT_AVAILABLE:
            row.append(str(declination_value))
        if hour_angle_value is not NOT_AVAILABLE:
            row.append(str(hour_angle_value))
        if position_algorithm is not NOT_AVAILABLE:
            row.append(position_algorithm)
        if zenith_value is not NOT_AVAILABLE:
            row.append(str(zenith_value))
        if altitude_value is not NOT_AVAILABLE:
            row.append(str(altitude_value))
        if azimuth_value is not NOT_AVAILABLE:
            row.append(str(azimuth_value))
        if incidence_value is not NOT_AVAILABLE:
            row.append(str(incidence_value))
        row.append(str(units))

        style_map = {
            "pvis": "red",  # red because PVIS is incomplete!
            "pvlib": "bold",
        }
        style = style_map.get(position_algorithm.lower(), None)
        table.add_row(*row, style=style)

    console = Console()
    console.print(table)


def print_solar_position_series_table(
    longitude,
    latitude,
    timestamps,
    timezone,
    table,
    index: bool = False,
    timing=None,
    declination=None,
    hour_angle=None,
    zenith=None,
    altitude=None,
    azimuth=None,
    surface_tilt=None,
    surface_orientation=None,
    incidence=None,
    user_requested_timestamps=None,
    user_requested_timezone=None,
    rounding_places=ROUNDING_PLACES_DEFAULT,
    group_models=False,
):
    longitude = round_float_values(longitude, rounding_places)
    latitude = round_float_values(latitude, rounding_places)
    rounded_table = round_float_values(table, rounding_places)

    quantities = [declination, zenith, altitude, azimuth, incidence]

    columns = []
    if index:
        columns.append("Index")
    # if longitude is not None:
    #     columns.append(LONGITUDE_COLUMN_NAME)
    # if latitude is not None:
    #     columns.append(LATITUDE_COLUMN_NAME)
    if timestamps is not None:
        columns.append('Time')
    # if timezone is not None:
    #     columns.append('Zone')
    # if user_requested_timestamps is not None and user_requested_timezone is not None:
    #     columns.extend(["Local Time", "Local Zone"])
    if timing is not None:
        columns.append(TIME_ALGORITHM_COLUMN_NAME)
    if declination is not None:
        columns.append(DECLINATION_COLUMN_NAME)
    if hour_angle is not None:
        columns.append(HOUR_ANGLE_COLUMN_NAME)
    if any(quantity is not None for quantity in quantities):
        columns.append(POSITION_ALGORITHM_COLUMN_NAME)
    if zenith is not None:
        columns.append(ZENITH_COLUMN_NAME)
    if altitude is not None:
        columns.append(ALTITUDE_COLUMN_NAME)
    if azimuth is not None:
        columns.append(AZIMUTH_COLUMN_NAME)
    if incidence is not None:
        # columns.append(SURFACE_TILT_COLUMN_NAME)
        # columns.append(SURFACE_ORIENTATION_COLUMN_NAME)
        columns.append(INCIDENCE_COLUMN_NAME)
    columns.append(UNITS_COLUMN_NAME)

    title = 'Solar geometry overview'
    caption = f"{LONGITUDE_COLUMN_NAME}, {LATITUDE_COLUMN_NAME} = [bold]{longitude}[/bold], [bold]{latitude}[/bold], "
    caption += f"Zone : {timezone}, "
    if (
        user_requested_timestamps is not None
        and user_requested_timezone is not None
    ):
        caption += f"Local zone : {user_requested_timezone}"
           # [
           #     str(user_requested_timestamps.get_loc(timestamp)),
           #     str(user_requested_timezone),
           # ]
    # Should be the same in case of multiple models!
    first_model = next(iter(rounded_table))

    surface_tilt = rounded_table[first_model].get(SURFACE_TILT_NAME, None) if surface_tilt else None
    caption += f"\nTilt : [bold]{surface_tilt}[/bold], "

    surface_orientation = rounded_table[first_model].get(SURFACE_ORIENTATION_NAME, None) if surface_orientation else None
    caption += f"Orientation : [bold]{surface_orientation}[/bold], "

    incidence_angle_definition = rounded_table[first_model].get(INCIDENCE_DEFINITION, None) if incidence else None
    caption += f"Incidence definition : [bold]{incidence_angle_definition}[/bold]"

    table = Table(
        *columns,
        title=title,
        caption=caption,
        box=box.SIMPLE_HEAD,
    )

    # Iterate over each timestamp and its corresponding result
    for model_name, model_result in rounded_table.items():
        for _index, timestamp in enumerate(timestamps):
            timing_algorithm = safe_get_value(model_result, TIME_ALGORITHM_NAME, NOT_AVAILABLE)  # If timing is a single value and not a list
            declination_value = safe_get_value(model_result, DECLINATION_NAME, _index) if declination else None
            hour_angle_value = safe_get_value(model_result, HOUR_ANGLE_NAME, _index) if hour_angle else None
            position_algorithm = safe_get_value(model_result, POSITION_ALGORITHM_NAME, NOT_AVAILABLE)
            zenith_value = safe_get_value(model_result, ZENITH_NAME, _index) if zenith else None
            altitude_value = safe_get_value(model_result, ALTITUDE_NAME, _index) if altitude else None
            azimuth_value = safe_get_value(model_result, AZIMUTH_NAME, _index) if azimuth else None
            # surface_tilt = safe_get_value(model_result, SURFACE_TILT_NAME, _index) if surface_tilt else None
            # surface_orientation = safe_get_value(model_result, SURFACE_ORIENTATION_NAME, _index) if surface_orientation else None
            incidence_value = safe_get_value(model_result, INCIDENCE_NAME, _index) if incidence else None
            units = safe_get_value(model_result, UNITS_NAME, UNITLESS)

            row = []
            if index:
                row.append(str(_index))
            # if longitude:
            #     row.append(str(longitude))
            # if latitude:
            #     row.append(str(latitude))
            # row.extend([str(timestamp), str(timezone)])
            row.extend([str(timestamp)])
            
           # ---------------------------------------------------- Implement-Me---
           # Convert the result back to the user's time zone
           # output_timestamp = output_timestamp.astimezone(user_timezone)
           # --------------------------------------------------------------------

           ## Redesign Me! =======================================================
           # if (
           #     user_requested_timestamps is not None
           #     and user_requested_timezone is not None
           # ):
           #     row.extend(
           #         [
           #             str(user_requested_timestamps.get_loc(timestamp)),
           #             str(user_requested_timezone),
           #         ]
           #     )
           ##=====================================================================

            if timing is not None:
                row.append(timing_algorithm)
            if declination_value is not None:
                row.append(str(declination_value))
            if hour_angle_value is not None:
                row.append(str(hour_angle_value))
            if position_algorithm is not None:
                row.append(position_algorithm)
            if zenith_value is not None:
                row.append(str(zenith_value))
            if altitude_value is not None:
                row.append(str(altitude_value))
            if azimuth_value is not None:
                row.append(str(azimuth_value))
            if incidence_value is not None:
                # if surface_tilt is not None:
                #     row.append(str(surface_tilt))
                # if surface_orientation is not None:
                #     row.append(str(surface_orientation))
                row.append(str(incidence_value))
            row.append(str(units))

            style_map = {
                "pvis": "red",  # red because PVIS is incomplete!
                "pvlib": "bold",
            }
            style = style_map.get(position_algorithm.lower(), None)
            table.add_row(*row, style=style)
        if group_models:
            table.add_row()

    console = Console()
    console.print(table)


def print_hour_angle_table_2(
    solar_time,
    rounding_places,
    hour_angle=None,
    units=None,
):
    """ """
    solar_time = round_float_values(solar_time, rounding_places)
    hour_angle = round_float_values(hour_angle, rounding_places)

    columns = [SOLAR_TIME_COLUMN_NAME]
    if hour_angle is not None:
        columns.append(HOUR_ANGLE_COLUMN_NAME)
    columns.append(UNITS_COLUMN_NAME)

    # table = Table(*columns, box=box.SIMPLE_HEAD)
    table = Table(
        *columns,
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold magenta",
    )

    row = [str(solar_time)]
    if hour_angle is not None:
        row.append(str(hour_angle))
    row.append(str(units))
    # table.add_row(*row, style=style)
    table.add_row(*row)

    console = Console()
    console.print(table)


def print_hour_angle_table(
    latitude,
    rounding_places,
    surface_tilt=None,
    declination=None,
    hour_angle=None,
    units=None,
):
    """ """
    console = Console()

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

    # table = Table(*columns, box=box.SIMPLE_HEAD)
    table = Table(
        *columns,
        box=box.SIMPLE_HEAD,
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
    # table.add_row(*row, style=style)
    table.add_row(*row)

    console.print(table)


def print_noaa_solar_position_table(
    longitude: float, 
    latitude: float, 
    timestamp: datetime, 
    timezone: str, 
    solar_position_calculations: dict,
    rounding_places: int = 5,
    user_requested_timestamp: datetime = None, 
    user_requested_timezone: str = None,
    angle_output_units: str = RADIANS,
    verbose: bool = False,  # New verbose argument
):
    console = Console()

    # Round off longitude, latitude and solar position calculations
    longitude = round_float_values(longitude, rounding_places)
    latitude = round_float_values(latitude, rounding_places)
    rounded_solar_position_calculations = round_float_values(solar_position_calculations, rounding_places)

    solar_position_table = Table(
        "Longitude",
        "Latitude",
        "Time",
        "Zone",
        "Model",
        # solar_position_calculations['fractional_year']
        # solar_position_calculations['equation_of_time']
        # solar_position_calculations['solar_declination']
        "Offset",
        # solar_position_calculations['time_offset']
        # solar_position_calculations['true_solar_time']
        # solar_position_calculations['solar_hour_angle']
        # solar_position_calculations['solar_zenith']
        ALTITUDE_COLUMN_NAME,
        AZIMUTH_COLUMN_NAME,
        "Sunrise",
        'Noon',
        'Local solar time',
        "Sunset",
        box=box.SIMPLE_HEAD,
    )
    solar_position_table.add_row(
        str(longitude),
        str(latitude),
        str(timestamp),
        str(timezone),
        "NOAA",  # Model name
        str(solar_position_calculations['time_offset'].value),
        str(convert_to_degrees_if_requested(rounded_solar_position_calculations['solar_altitude'].value,
                                            angle_output_units)),
        str(rounded_solar_position_calculations['solar_azimuth'].value),
        str(solar_position_calculations['sunrise_time']),
        str(solar_position_calculations['noon_time']),
        str(solar_position_calculations['local_solar_time']),
        str(solar_position_calculations['sunset_time']),
    )

    if user_requested_timestamp is not None and user_requested_timezone is not None:
        solar_position_table = Table(
            "Longitude",
            "Latitude",
            "Time",
            "Zone",
            "Local Time",
            "Local Zone",
            "Model",
          # solar_position_calculations['fractional_year']
          # solar_position_calculations['equation_of_time']
          # solar_position_calculations['solar_declination']
          # solar_position_calculations['time_offset']
            "Offset",
          # solar_position_calculations['true_solar_time']
          # solar_position_calculations['solar_hour_angle']
          # solar_position_calculations['solar_zenith']
            ALTITUDE_COLUMN_NAME,
            AZIMUTH_COLUMN_NAME,
            "Sunrise",
            'Noon',
            'Local solar time',
            "Sunset",
            box=box.SIMPLE_HEAD,
        )
        solar_position_table.add_row(
            str(longitude),
            str(latitude),
            str(timestamp),
            str(timezone),
            str(user_requested_timestamp),
            str(user_requested_timezone),
            "NOAA",  # Model name
            str(solar_position_calculations['time_offset']),
            str(rounded_solar_position_calculations['solar_altitude']),
            str(rounded_solar_position_calculations['solar_azimuth']),
            str(solar_position_calculations['sunrise_time']),
            str(solar_position_calculations['noon_time']),
            str(solar_position_calculations['local_solar_time']),
            str(solar_position_calculations['sunset_time']),
        )

    console.print(solar_position_table)

    if verbose:
        verbose_info = f"""
            Fractional Year: {solar_position_calculations['fractional_year']}
            Equation of Time: {solar_position_calculations['equation_of_time']}
            Solar Declination: {solar_position_calculations['solar_declination']}
            Time Offset: {solar_position_calculations['time_offset']}
            True Solar Time: {solar_position_calculations['true_solar_time']}
            Solar Hour Angle: {solar_position_calculations['solar_hour_angle']}
            Solar Zenith: {solar_position_calculations['solar_zenith']} """
        console.print(Panel(verbose_info, title="Verbose Information"))


def print_quantity_table(
    dictionary: dict = dict(),
    title: str ='Series',
    main_key: str = None,
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    verbose=1,
    index: bool = False,
):
    console = Console()
    table = Table(title=title, box=box.SIMPLE_HEAD)
    
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
            from rich.text import Text
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
        console.print(table)


def print_irradiance_table_2(
    longitude=None,
    latitude=None,
    timestamps: datetime = [datetime.now()],
    dictionary: dict = dict(),
    title: str ='Irradiance series',
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    verbose=1,
    index: bool = False,
):
    console = Console()
    caption = f"{LONGITUDE_COLUMN_NAME}, {LATITUDE_COLUMN_NAME} = [bold]{longitude}[/bold], [bold]{latitude}[/bold], "
    caption += f"\n⌁ : Power, "
    caption += f"⭍ : Effective component, "
    caption += f"🗤 : Diffuse, "
    caption += f"☈ : Reflected, "
    caption += f"∡ : On inclined plane, "
    caption += f"↻ : Orientation\n"
    table = Table(
            title=title,
            caption=caption,
            box=box.SIMPLE_HEAD,
            )
    
    if index:
        table.add_column("Index")

    # base columns
    # if verbose > 0:
    #     if longitude:
    #         table.add_column('Longitude')
    #     if latitude:
    #         table.add_column('Latitude')
    table.add_column('Time')
    
    # remove the 'Title' entry! ---------------------------------------------
    dictionary.pop('Title', NOT_AVAILABLE)
    # ------------------------------------------------------------- Important

    # additional columns based dictionary keys
    for key in dictionary.keys():
        if dictionary[key] is not None:
            table.add_column(key)
    
    # Convert single float, int or str values to arrays of the same length as timestamps
    for key, value in dictionary.items():
        if isinstance(value, (float, int)):
            dictionary[key] = np.full(len(timestamps), value)

        if isinstance(value, str):
            dictionary[key] = np.full(len(timestamps), str(value))
    
    # Zip series and timestamps
    zipped_series = zip(*dictionary.values())
    zipped_data = zip(timestamps, zipped_series)

    # Populate table
    index_counter = 1
    for timestamp, values in zipped_data:
        row = []

        if index:
            row.append(str(index_counter))
            index_counter += 1

        # if verbose > 0 and longitude and latitude:
        #     row.append(round_float_values(longitude, rounding_places))
        #     row.append(round_float_values(latitude, rounding_places))

        row.append(to_datetime(timestamp).strftime('%Y-%m-%d %H:%M:%S'))

        for idx, (column_name, value) in enumerate(zip(dictionary.keys(), values)):
            from rich.text import Text
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
        console.print(table)
