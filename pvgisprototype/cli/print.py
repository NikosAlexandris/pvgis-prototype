from devtools import debug
from datetime import datetime
from ..api.utilities.conversions import convert_to_degrees_if_requested
from ..api.utilities.conversions import round_float_values
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import List
from pvgisprototype.constants import (
    POSITION_ALGORITHM_COLUMN_NAME,
    POSITION_ALGORITHM_NAME,
    ALTITUDE_COLUMN_NAME,
    ALTITUDE_NAME,
    AZIMUTH_COLUMN_NAME,
    AZIMUTH_NAME,
    DECLINATION_COLUMN_NAME,
    DECLINATION_NAME,
    HOUR_ANGLE_COLUMN_NAME,
    HOUR_ANGLE_NAME,
    INCIDENCE_COLUMN_NAME,
    INCIDENCE_NAME,
    TIME_ALGORITHM_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    UNITS_COLUMN_NAME,
    UNITS_NAME,
    ZENITH_COLUMN_NAME,
    ZENITH_NAME,
    NOT_AVAILABLE_COLUMN_NAME,
    UNITLESSS_COLUMN_NAME,
)


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
    rounding_places,
    declination=None,
    hour_angle=None,
    zenith=None,
    altitude=None,
    azimuth=None,
    incidence=None,
    user_requested_timestamp=None,
    user_requested_timezone=None,
):
    """ """
    console = Console()

    longitude = round_float_values(longitude, rounding_places)
    latitude = round_float_values(latitude, rounding_places)
    rounded_table = round_float_values(table, rounding_places)

    columns = ["Longitude", "Latitude", "Time", "Zone"]
    if user_requested_timestamp and user_requested_timezone:
        columns.extend(["Local Time", "Local Zone"])
    columns.append(TIME_ALGORITHM_COLUMN_NAME)
    if declination is not None:
        columns.append(DECLINATION_COLUMN_NAME)
    if hour_angle is not None:
        columns.append(HOUR_ANGLE_COLUMN_NAME)
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

    for model_result in rounded_table:
        algorithm_name = model_result.get(POSITION_ALGORITHM_NAME, '')
        declination_value = model_result.get(DECLINATION_NAME, NOT_AVAILABLE_COLUMN_NAME) if declination is not None else None
        hour_angle_value = model_result.get(HOUR_ANGLE_NAME, NOT_AVAILABLE_COLUMN_NAME) if hour_angle is not None else None
        zenith_value = model_result.get(ZENITH_NAME, NOT_AVAILABLE_COLUMN_NAME) if zenith is not None else None
        altitude_value = model_result.get(ALTITUDE_NAME, NOT_AVAILABLE_COLUMN_NAME) if altitude is not None else None
        azimuth_value = model_result.get(AZIMUTH_NAME, NOT_AVAILABLE_COLUMN_NAME) if azimuth is not None else None
        incidence_value = model_result.get(INCIDENCE_NAME, NOT_AVAILABLE_COLUMN_NAME) if incidence is not None else None
        units = model_result.get(UNITS_NAME, UNITLESSS_COLUMN_NAME)
        solar_time_model = model_result.get(TIME_ALGORITHM_NAME, '')

        row = [str(longitude), str(latitude), str(timestamp), str(timezone)]

       # ---------------------------------------------------- Implement-Me---
       # Convert the result back to the user's time zone
       # output_timestamp = output_timestamp.astimezone(user_timezone)
       # --------------------------------------------------------------------

       # Redesign Me! =======================================================
        if user_requested_timestamp and user_requested_timezone:
            row.extend([str(user_requested_timestamp), str(user_requested_timezone)])
       #=====================================================================

        is_pvis = solar_time_model.lower() == 'pvis'
        style = "red" if is_pvis else None
        is_pvlib = solar_time_model.lower() == 'pvlib'
        style = "bold" if is_pvlib else None
        row.append(solar_time_model)
        if declination_value is not None:
            row.append(str(declination_value))
        if hour_angle_value is not None:
            row.append(str(hour_angle_value))
        row.append(algorithm_name)
        if zenith_value is not None:
            row.append(str(zenith_value))
        if altitude_value is not None:
            row.append(str(altitude_value))
        if azimuth_value is not None:
            row.append(str(azimuth_value))
        if incidence_value is not None:
            row.append(str(incidence_value))

        row.append(str(units))
        table.add_row(*row, style=style)

    console.print(table)


def print_hour_angle_table_2(
    solar_time,
    rounding_places,
    hour_angle=None,
    units=None,
):
    """ """
    console = Console()

    solar_time = round_float_values(solar_time, rounding_places)
    hour_angle = round_float_values(hour_angle, rounding_places)

    columns = ["Solar time"]
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
    angle_output_units: str = 'radians',
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
