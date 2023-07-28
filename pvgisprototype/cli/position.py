from devtools import debug
from pvgisprototype.cli.debug import debug_if_needed

"""
Important sun and solar surface geometry parameters in calculating the amount of solar radiation that reaches a particular location on the Earth's surface
"""

import typer
from typing import Annotated
from typing import Optional
from typing import Union
from typing import List
from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime
from zoneinfo import ZoneInfo
import math
from math import radians
import numpy as np
from ..api.utilities.timestamp import now_utc_datetimezone
from ..api.utilities.timestamp import now_local_datetimezone
from ..api.utilities.timestamp import ctx_convert_to_timezone
from ..api.utilities.timestamp import attach_timezone
from ..api.utilities.timestamp import convert_hours_to_seconds
from ..api.utilities.timestamp import convert_hours_to_datetime_time
from ..api.utilities.timestamp import random_datetimezone
from ..api.utilities.timestamp import ctx_attach_requested_timezone
from ..api.utilities.conversions import convert_to_radians
from ..api.utilities.conversions import convert_to_degrees_if_requested
from ..api.utilities.conversions import round_float_values
from ..api.geometry.solar_declination import calculate_solar_declination
from ..models.standard.solar_incidence import calculate_solar_incidence
from ..models.jenco.solar_incidence import calculate_solar_incidence_jenco
from ..models.jenco.solar_incidence import calculate_effective_solar_incidence_angle
from ..models.pyephem.solar_time import calculate_solar_time_ephem
from ..api.geometry.solar_hour_angle import calculate_hour_angle
from ..api.geometry.solar_hour_angle import calculate_hour_angle_sunrise
from ..api.geometry.solar_azimuth import calculate_solar_azimuth
from ..api.geometry.solar_models import SolarPositionModels
from ..api.geometry.solar_position import _parse_model
from ..api.geometry.solar_position import calculate_solar_position
from ..api.geometry.solar_position import model_solar_position
from ..models.noaa.solar_position import calculate_noaa_solar_position
from .rich_help_panel_names import rich_help_panel_geometry_time
from .rich_help_panel_names import rich_help_panel_geometry_position
from .rich_help_panel_names import rich_help_panel_geometry_refraction
from .rich_help_panel_names import rich_help_panel_geometry_surface

from pvgisprototype.api.input_models import HourAngleInput
from pvgisprototype.api.input_models import HourAngleSunriseInput

from .print import print_table
from .print import print_solar_position_table
from .print import print_noaa_solar_position_table
from pvgisprototype.api.input_models import SolarDeclinationInput


console = Console()
app = typer.Typer(
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":triangular_ruler:  Calculate solar geometry parameters for a location and moment in time",
)


state = {"verbose": False}
@app.callback()
def main(
        ctx: typer.Context,
        verbose: bool = False,
        ):
    """
    Solar position algorithms
    """
    # print(f"Executing command: {ctx.invoked_subcommand}")
    if verbose:
        print("Will output verbosely")
        state["verbose"] = True



@app.command(
        no_args_is_help=True,
        help=':sun: :clock12: :triangular_ruler: NOAA\'s general solar position calculations',
)
@debug_if_needed(app)
def noaa(
        ctx: typer.Context,
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        refracted_solar_zenith: float = 1.5853349194640094,  # radians
        apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
            '-a',
            '--atmospheric-refraction',
            help='Apply atmospheric refraction functions',
            )] = True,
        time_output_units: Annotated[str, typer.Option(
            '--time-output-units',
            show_default=True,
            case_sensitive=False,
            help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]")] = 'minutes',
        angle_units: Annotated[str, typer.Option(
            '--angle-units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for internal calculations (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--angle-output-units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for solar position calculations output (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        rounding_places: Annotated[Optional[int], typer.Option(
            '-r',
            '--rounding-places',
            show_default=True,
            help='Number of places to round results to.')] = 5,
        verbose: bool = False,
        ):
    """
    """
    # Initialize with None ---------------------------------------------------
    user_requested_timestamp = None
    user_requested_timezone = None
    # -------------------------------------------- Smarter way to do this? ---
    
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        timezone = utc_zoneinfo
        typer.echo(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')

    solar_position_calculations = calculate_noaa_solar_position(
            longitude,
            latitude,
            timestamp,
            timezone,
            refracted_solar_zenith,
            apply_atmospheric_refraction,
            time_output_units,
            angle_units,
            angle_output_units,
            )
    # Convert output timestamp back to the user-requested timezone
    try:
        timestamp = user_requested_timestamp
        timezone = user_requested_timezone
    except:
        print(f'I guess there where no user requested timestamp and zone')

    print_noaa_solar_position_table(
        longitude,
        latitude,
        timestamp,
        timezone,
        solar_position_calculations, 
        rounding_places, 
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )

# @app.callback(
#         'all',
#         invoke_without_command=True,
@app.command(
        'overview',
        no_args_is_help=True,
        help='⦩⦬ Calculate solar position parameters (altitude, azimuth)',
 )
@debug_if_needed(app)
def position(
        ctx: typer.Context,
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        model: Annotated[List[SolarPositionModels], typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            # callback=_parse_model,
            help="Model(s) to calculate solar position.")] = [SolarPositionModels.skyfield],
        apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
            '-a',
            '--atmospheric-refraction',
            help='Apply atmospheric refraction functions',
            )] = True,
        time_output_units: Annotated[str, typer.Option(
            '-u',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]")] = 'minutes',
        angle_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for internal calculations (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for solar position calculations output (degrees or radians)")] = 'radians',
        rounding_places: Annotated[Optional[int], typer.Option(
            '-r',
            '--rounding-places',
            show_default=True,
            help='Number of places to round results to.')] = 5,
        verbose: bool = False,
        ):
    """
    """
    # print(f'Context: {ctx}')
    # print(f'Context: {ctx.params}')
    # print(f"Invoked subcommand: {ctx.invoked_subcommand}")

    # if ctx.invoked_subcommand is not None:
    #     print("Skipping default command to run sub-command.")
    #     return

    # elif ctx.invoked_subcommand in ['altitude', 'azimuth']:
    #     print('Execute subcommand')

    # else:
    #     print('Yay')
    #     return

    # Initialize with None ---------------------------------------------------
    user_requested_timestamp = None
    user_requested_timezone = None
    # -------------------------------------------- Smarter way to do this? ---
    
    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        timezone = utc_zoneinfo
        typer.echo(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')
    
    # Why does the callback function `_parse_model` not work? 
    if SolarPositionModels.all in model:
        model = [model for model in SolarPositionModels if model != SolarPositionModels.all]

    solar_position = calculate_solar_position(
            longitude,
            latitude,
            timestamp,
            timezone,
            model,
            apply_atmospheric_refraction,
            time_output_units,
            angle_units,
            angle_output_units,
            )
    longitude = convert_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_to_degrees_if_requested(latitude, angle_output_units)
    print_solar_position_table(
        longitude,
        latitude,
        timestamp,
        timezone,
        solar_position,
        rounding_places,
        altitude=True,
        azimuth=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
    )


@app.command('altitude', no_args_is_help=True, help='⦩ Calculate the solar altitude')
@debug_if_needed(app)
def altitude(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        model: Annotated[List[SolarPositionModels], typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            # callback=_parse_model,
            help="Model(s) to calculate solar position.")] = [SolarPositionModels.skyfield],
        apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
            '-a',
            '--atmospheric-refraction',
            help='Apply atmospheric refraction functions',
            )] = False,
        time_output_units: Annotated[str, typer.Option(
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]")] = 'minutes',
        angle_units: Annotated[str, typer.Option(
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for internal calculations (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for solar position calculations output (degrees or radians)")] = 'radians',
        rounding_places: Annotated[Optional[int], typer.Option(
            '-r',
            '--rounding-places',
            show_default=True,
            help='Number of places to round results to.')] = 5,
        verbose: bool = False,
        ) -> float:
    """Compute various solar geometry variables.

    The solar altitude angle (SAA) is the complement of the solar zenith angle,
    measuring from the horizon directly below the sun to the sun itself. An
    altitude of 0 degrees means the sun is on the horizon, and an altitude of
    90 degrees means the sun is directly overhead.

    Parameters
    ----------
    solar_geometry_day_constants : SolarGeometryDayConstants
        The input solar geometry constants.
    """
    # Initialize with None ---------------------------------------------------
    user_requested_timestamp = None
    user_requested_timezone = None
    # -------------------------------------------- Smarter way to do this? ---

    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        typer.echo(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')
    
    # Why does the callback function `_parse_model` not work? ----------------
    if SolarPositionModels.all in model:
        model = [
            model for model in SolarPositionModels if model != SolarPositionModels.all
        ]
    solar_position = calculate_solar_position(
        longitude,
        latitude,
        timestamp,
        timezone,
        model,
        apply_atmospheric_refraction,
        time_output_units,
        angle_units,
        angle_output_units,
    )
    print_solar_position_table(
        longitude,
        latitude,
        timestamp,
        timezone,
        solar_position,
        rounding_places,
        altitude=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
    )


@app.command('zenith', no_args_is_help=True, help=' Calculate the solar zenith')
@debug_if_needed(app)
def zenith(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        model: Annotated[List[SolarPositionModels], typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            # callback=_parse_model,
            help="Model(s) to calculate solar position.")] = [SolarPositionModels.skyfield],
        apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
            '-a',
            '--atmospheric-refraction',
            help='Apply atmospheric refraction functions',
            )] = False,
        time_output_units: Annotated[str, typer.Option(
            '-u',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]")] = 'minutes',
        angle_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for internal calculations (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for solar position calculations output (degrees or radians)")] = 'radians',
        rounding_places: Annotated[Optional[int], typer.Option(
            '-r',
            '--rounding-places',
            show_default=True,
            help='Number of places to round results to.')] = 5,
        verbose: bool = False,
        ) -> float:
    """Calculate the solar zenith angle

    The solar zenith angle (SZA) is the angle between the zenith (directly
    overhead) and the line to the sun. A zenith angle of 0 degrees means the
    sun is directly overhead, while an angle of 90 degrees means the sun is on
    the horizon.

    Parameters
    ----------
    solar_geometry_day_constants : SolarGeometryDayConstants
        The input solar geometry constants.
    """
    # Initialize with None ---------------------------------------------------
    user_requested_timestamp = None
    user_requested_timezone = None
    # -------------------------------------------- Smarter way to do this? ---

    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        typer.echo(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')

    # Why does the callback function `_parse_model` not work? ----------------
    if SolarPositionModels.all in model:
        model = [
            model for model in SolarPositionModels if model != SolarPositionModels.all
        ]
    solar_position = calculate_solar_position(
        longitude,
        latitude,
        timestamp,
        timezone,
        model,
        apply_atmospheric_refraction,
        time_output_units,
        angle_units,
        angle_output_units,
    )
    for model_result in solar_position:
        solar_altitude = model_result.get('Altitude', None)
        if solar_altitude is not None:
            if angle_output_units == 'degrees':
                model_result['Zenith'] = 90 - solar_altitude
            else:
                model_result['Zenith'] = radians(90) - solar_altitude
    print_solar_position_table(
        longitude,
        latitude,
        timestamp,
        timezone,
        solar_position,
        rounding_places,
        zenith=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
    )


@app.command('azimuth', no_args_is_help=True, help='⦬ Calculate the solar azimuth')
@debug_if_needed(app)
def azimuth(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        days_in_a_year: float = 365.25,
        perigee_offset: float = 0.048869,
        orbital_eccentricity: float = 0.01672,
        hour_offset: float = 0,
        model: Annotated[List[SolarPositionModels], typer.Option(
            '-m',
            '--model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            # callback=_parse_model,
            help="Model(s) to calculate solar position.")] = [SolarPositionModels.skyfield],
        apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
            '-a',
            '--atmospheric-refraction',
            help='Apply atmospheric refraction functions',
            )] = False,
        time_output_units: Annotated[str, typer.Option(
            '-u',
            '--output-units',
            show_default=True,
            case_sensitive=False,
            help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]")] = 'minutes',
        angle_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for internal calculations (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for the calculated solar azimuth output (degrees or radians)")] = 'radians',
        rounding_places: Annotated[Optional[int], typer.Option(
            '-r',
            '--rounding-places',
            show_default=True,
            help='Number of places to round results to.')] = 5,
        verbose: bool = False,
        ) -> float:
    """Calculate the solar azimuth angle

    The solar azimuth angle (Az) specifies the east-west orientation of the
    sun. It is usually measured from the south, going positive to the west. The
    exact definitions can vary, with some sources defining the azimuth with
    respect to the north, so care must be taken to use the appropriate
    convention.

    Parameters
    ----------

    Returns
    -------
    solar_azimuth: float
    """
    # Initialize with None ---------------------------------------------------
    user_requested_timestamp = None
    user_requested_timezone = None
    # -------------------------------------------- Smarter way to do this? ---

    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        typer.echo(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')

    # Why does the callback function `_parse_model` not work? ----------------
    if SolarPositionModels.all in model:
        model = [
            model for model in SolarPositionModels if model != SolarPositionModels.all
        ]
    solar_position = calculate_solar_position(
        longitude,
        latitude,
        timestamp,
        timezone,
        model,
        apply_atmospheric_refraction,
        time_output_units,
        angle_units,
        angle_output_units,
    )
    print_solar_position_table(
        longitude,
        latitude,
        timestamp,
        timezone,
        solar_position,
        rounding_places,
        azimuth=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
    )


@app.command('declination', no_args_is_help=True, help='∢ Calculate the solar declination')
def declination(
        timestamp: Annotated[datetime, typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        local: Annotated[bool, typer.Option(
            help='Use the system\'s local time zone',
            callback=now_local_datetimezone)] = False,
        days_in_a_year: float = 365.25,
        orbital_eccentricity: float = 0.03344,
        perigee_offset: float = 0.048869,
        angle_output_units: Annotated[Optional[str], typer.Option(
            '-u',
            '--angle-output-units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for solar position calculations output (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        random_time: Annotated[bool, typer.Option(
            '-r',
            '--random',
            '--random-time',
            help="Generate a random date, time and timezone to demonstrate calculation")] = False,
        ) -> float:
    """Calculat the solar declination angle 

    The solar declination (delta) is the angle between the line from the Earth
    to the Sun and the plane of the Earth's equator. It varies between ±23.45
    degrees over the course of a year as the Earth orbits the Sun.

    Parameters
    ----------

    Returns
    -------
    solar_declination: float
    """
    # Possible to move to a callback? ----------------------------------------
    if random_time:
        timestamp, timezone = random_datetimezone()
    # ------------------------------------------------------------------------

    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        typer.echo(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')

    solar_declination = calculate_solar_declination(
            timestamp=timestamp,
            timezone=timezone,
            days_in_a_year=days_in_a_year,
            orbital_eccentricity=orbital_eccentricity,
            perigee_offset=perigee_offset,
            angle_output_units=angle_output_units,
    )

    solar_declination = convert_to_degrees_if_requested(
            solar_declination,
            angle_output_units)

    # table = Table(show_header=True, header_style="bold magenta")
    # table.add_column("Date, time and zone")
    # table.add_column("Solar declination")
    # table.add_column("Units")
    # table.add_row(str(timestamp), str(solar_declination), str(angle_output_units))

    headers = [
            "Date, time, zone",
            "Solar declination",
            "Units"
            ]
    data = [
            [str(timestamp),
             str(solar_declination),
             str(angle_output_units)]
            ]
    print_table(headers, data)

@app.command('surface-orientation', no_args_is_help=True, help=':compass: Calculate the solar surface orientation (azimuth)')
def surface_orientation():
    """Calculate the surface azimuth angle

    The surface azimuth or orientation (also known as Psi) is the angle between
    the projection on a horizontal plane of the normal to a surface and the
    local meridian, with north through east directions being positive.
    """

    #
    # Update Me
    #

    pass


@app.command('surface-tilt', no_args_is_help=True, help='Calculate the solar surface tile (slope)')
def surface_tilt():
    """Calculate the surface tilt angle

    The surface tilt (or slope, also known as beta) is the angle between the
    plane of the surface and the horizontal plane. A horizontal surface has a
    slope of 0°, and a vertical surface has a slope of 90°.
    """

    #
    # Update Me
    #

    pass


@app.command('incidence', no_args_is_help=True, help='Calculate the solar incidence angle')
def incidence(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        solar_declination: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        surface_tilt: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        surface_orientation: Annotated[Optional[float], typer.Argument(
            min=0, max=360)] = 180,
        hour_angle: Annotated[Optional[float], typer.Argument(
            min=0, max=1)] = None,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar incidence angle (degrees or radians)")] = 'radians',
        ):
    """Calculate the angle of incidence

    The angle of incidence (also known as theta) is the angle between the
    direct beam of sunlight and the line perpendicular (normal) to the surface.
    If the sun is directly overhead and the surface is flat (horizontal), the
    angle of incidence is 0°.
    """

    #
    # Update Me
    #

    import random

    if not surface_tilt:
        surface_tilt = random.uniform(0, 90)  # Returns a random floating point number in the range [0, 90)

    if not surface_orientation:
        surface_orientation = random.uniform(0, 360)  # Returns a random floating point number in the range [0, 360)

    return None


@app.command('incidence-jenco', no_args_is_help=True, help='Calculate the solar incidence angle')
def incidence_jenco(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone,
            callback=ctx_attach_requested_timezone,
            )],
        timezone: Annotated[Optional[str], typer.Option(
            help='Specify timezone (e.g., "Europe/Athens"). Use "local" to use the system\'s time zone',
            callback=ctx_convert_to_timezone)] = None,
        random_time: Annotated[bool, typer.Option(
            '-r',
            '--random',
            '--random-time',
            help="Generate a random date, time and timezone to demonstrate calculation")] = False,
        hour_angle: Annotated[float, typer.Argument(
            help="Solar hour angle in radians")] = None,
        surface_tilt: Annotated[float, typer.Argument(
            help="Tilt of the surface in degrees")] = None,
        surface_orientation: Annotated[float, typer.Argument(
            help="Orientation of the surface (azimuth angle in degrees)")] = None,
        days_in_a_year: float = 365.25,
        orbital_eccentricity: float = 0.03344,
        perigee_offset: float = 0.048869,
        time_output_units: Annotated[str, typer.Option(
            '-u',
            '--time-output-units',
            show_default=True,
            case_sensitive=False,
            help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]")] = 'minutes',
        angle_units: Annotated[str, typer.Option(
            '-u',
            '--angle-units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for internal calculations (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--angle-output-units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for solar position calculations output (degrees or radians) - :warning: [bold red]Keep fingers away![/bold red]")] = 'radians',
        rounding_places: Annotated[Optional[int], typer.Option(
            '-r',
            '--rounding-places',
            show_default=True,
            help='Number of places to round results to.')] = 5,
        verbose: bool = False,
        ):
    """Calculate the angle of incidence

    The angle of incidence (also known as theta) is the angle between the
    direct beam of sunlight and the line perpendicular (normal) to the surface.
    If the sun is directly overhead and the surface is flat (horizontal), the
    angle of incidence is 0°.
    """

    # --------------------------------------------------------------- Idea ---
    # if not given, optimise tilt and orientation... ?
    # ------------------------------------------------------------------------
    import random

    if not surface_tilt:
        surface_tilt = random.uniform(0, 90)

    if not surface_orientation:
        surface_orientation = random.uniform(0, 360)

    solar_incidence_angle = calculate_solar_incidence_jenco(
        longitude,
        latitude,
        timestamp,
        timezone,
        random_time,
        hour_angle,
        surface_tilt,
        surface_orientation,
        days_in_a_year,
        orbital_eccentricity,
        perigee_offset,
        time_output_units,
        angle_units,
        angle_output_units,
        rounding_places,
        verbose,
    )

    typer.echo(f'Solar incidence angle {solar_incidence_angle} {angle_output_units}')


@app.command(
    'incidence-effective',
    no_args_is_help=True,
    help='Calculate the effective solar incidence angle considering shadows',
)
def incidence_jenco(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        solar_declination: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        surface_tilt: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        surface_orientation: Annotated[Optional[float], typer.Argument(
            min=0, max=360)] = 180,
        hour_angle: Annotated[Optional[float], typer.Argument(
            min=0, max=1)] = None,
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar incidence angle (degrees or radians)")] = 'radians',
        ):
    """Calculate the angle of incidence

    The angle of incidence (also known as theta) is the angle between the
    direct beam of sunlight and the line perpendicular (normal) to the surface.
    If the sun is directly overhead and the surface is flat (horizontal), the
    angle of incidence is 0°.
    """
    effective_solar_incidence_angle = calculate_effective_solar_incidence_angle(
        longitude,
        latitude,
        hour_angle,
        surface_tilt,
        surface_orientation,
        solar_azimuth,
        solar_altitude,
        shadow_indicator,
        horizon_heights,
        horizon_interval,
    )

    return effective_solar_incidence_angle


@app.command('hour-angle', no_args_is_help=True, help=':clock12: :globe_with_meridians: Calculate the hour angle (ω)')
def hour_angle(
        solar_time: Annotated[float, typer.Argument(
            help='The solar time in decimal hours on a 24 hour base',
            callback=convert_hours_to_datetime_time)],
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ):
    """Calculate the hour angle 'ω = (ST / 3600 - 12) * 15 * π / 180'

    The hour angle (ω) is the angle at any instant through which the earth has
    to turn to bring the meridian of the observer directly in line with the
    sun's rays measured in radian. In other words, it is a measure of time,
    expressed in angular measurement, usually degrees, from solar noon. It
    increases by 15° per hour, negative before solar noon and positive after
    solar noon.
    """

    #
    # Update Me
    #

    hour_angle = calculate_hour_angle(
        HourAngleInput(
            solar_time=solar_time,
            angle_output_units=output_units,
        )
    )
    typer.echo(f'Hour angle: {hour_angle.value} {hour_angle.unit}')              # FIXME: typer ?!


@app.command('sunrise', no_args_is_help=True, help=':sunrise: Calculate the hour angle (ω) at sun rise and set')
def hour_angle(
        latitude: Annotated[Optional[float], typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        surface_tilt: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        solar_declination: Annotated[Optional[float], typer.Argument(
            min=-90, max=90)] = 0,                                                  # XXX: Default value changed from 180 to 0
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        ):
    """Calculate the hour angle 'ω = (ST / 3600 - 12) * 15 * π / 180'

    The hour angle (ω) is the angle at any instant through which the earth has
    to turn to bring the meridian of the observer directly in line with the
    sun's rays measured in radian. In other words, it is a measure of time,
    expressed in angular measurement, usually degrees, from solar noon. It
    increases by 15° per hour, negative before solar noon and positive after
    solar noon.
    """

    #
    # Update Me
    #

    hour_angle = calculate_hour_angle_sunrise(
        HourAngleSunriseInput(
            latitude=latitude,
            surface_tilt=surface_tilt,
            solar_declination=solar_declination,
            angle_output_units=output_units,
        )
    )

    typer.echo(f'Solar time: {hour_angle.value} {hour_angle.unit}')              # FIXME: typer ?


if __name__ == "__main__":
    # import sys
    # commands = {'all', 'altitude', 'azimuth'}
    # sys.argv.insert(1, 'all') if sys.argv[1] not in commands else None
    app()
