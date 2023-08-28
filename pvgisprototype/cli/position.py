from devtools import debug
from pvgisprototype.cli.debug import debug_if_needed

"""
Important sun and solar surface geometry parameters in calculating the amount of solar radiation that reaches a particular location on the Earth's surface
"""

import typer
from typer.core import TyperGroup
from click import Context
from typing import Annotated
from typing import Optional
from typing import Union
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
import math
from math import radians
import numpy as np
# from rich.console import Console
from rich.table import Table
from rich import box
from .typer_parameters import OrderCommands
from .typer_parameters import typer_argument_longitude
from .typer_parameters import typer_argument_latitude
from .typer_parameters import typer_argument_timestamp
from .typer_parameters import typer_option_timezone
from .typer_parameters import typer_option_local_time
from .typer_parameters import typer_option_random_time
from .typer_parameters import typer_argument_solar_declination
from .typer_parameters import typer_argument_surface_tilt
from .typer_parameters import typer_argument_surface_orientation
from .typer_parameters import typer_argument_hour_angle
from .typer_parameters import typer_argument_solar_time
from .typer_parameters import typer_option_solar_position_model
from .typer_parameters import typer_option_solar_time_model
from .typer_parameters import typer_option_global_time_offset
from .typer_parameters import typer_option_hour_offset
from .typer_parameters import typer_option_days_in_a_year
from .typer_parameters import typer_option_perigee_offset
from .typer_parameters import typer_option_eccentricity_correction_factor
from .typer_parameters import typer_option_apply_atmospheric_refraction
from .typer_parameters import typer_option_refracted_solar_zenith
from .typer_parameters import typer_option_time_output_units
from .typer_parameters import typer_option_angle_units
from .typer_parameters import typer_option_angle_output_units
from .typer_parameters import typer_option_rounding_places
from .typer_parameters import typer_option_verbose
from ..api.utilities.timestamp import now_utc_datetimezone
from ..api.utilities.timestamp import now_local_datetimezone
from ..api.utilities.timestamp import ctx_convert_to_timezone
from ..api.utilities.timestamp import convert_hours_to_seconds
from ..api.utilities.timestamp import convert_hours_to_datetime_time
from ..api.utilities.timestamp import random_datetimezone
from ..api.utilities.timestamp import ctx_attach_requested_timezone
from ..api.utilities.conversions import convert_to_radians
from ..api.utilities.conversions import convert_to_degrees_if_requested
from ..api.utilities.conversions import convert_float_to_degrees_if_requested
from ..api.utilities.conversions import round_float_values
from ..api.geometry.solar_declination import calculate_solar_declination
from ..models.standard.solar_incidence import calculate_solar_incidence
from ..models.jenco.solar_incidence import calculate_solar_incidence_jenco
from ..models.jenco.solar_incidence import calculate_effective_solar_incidence_angle
from ..models.pyephem.solar_time import calculate_solar_time_ephem
from ..api.geometry.solar_hour_angle import calculate_hour_angle
from ..api.geometry.solar_hour_angle import calculate_hour_angle_sunrise
from ..api.geometry.solar_azimuth import calculate_solar_azimuth
from ..api.geometry.solar_position import SolarPositionModels
from ..api.geometry.time_models import SolarTimeModels
from ..api.geometry.solar_position import _parse_model
from ..api.geometry.solar_position import calculate_solar_position
from ..api.geometry.solar_position import model_solar_position
from ..models.noaa.solar_position import calculate_noaa_solar_position
from .rich_help_panel_names import rich_help_panel_advanced_options
from .rich_help_panel_names import rich_help_panel_geometry_time
from .rich_help_panel_names import rich_help_panel_geometry_position
from .rich_help_panel_names import rich_help_panel_geometry_refraction
from .rich_help_panel_names import rich_help_panel_geometry_surface
from .rich_help_panel_names import rich_help_panel_solar_time
from .rich_help_panel_names import rich_help_panel_earth_orbit
from .rich_help_panel_names import rich_help_panel_atmospheric_properties
from .rich_help_panel_names import rich_help_panel_output

from .print import print_table
from .print import print_solar_position_table
from .print import print_noaa_solar_position_table


# console = Console()
app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":triangular_ruler:  Calculate solar geometry parameters for a location and moment in time",
)
state = {"verbose": False}


@app.callback()
def main(
    ctx: typer.Context,
    verbose: Annotated[Optional[bool], typer.Option(
        help="Show details while executing commands")] = False,
    debug: Annotated[Optional[bool], typer.Option(
        "--debug",
        help="Enable debug mode")] = False,
):
    """
    Solar position algorithms
    """
    # print(f"Executing command: {ctx.invoked_subcommand}")
    if verbose:
        print("Will output verbosely")
        state["verbose"] = True

    app.debug_mode = debug


@app.command(
        no_args_is_help=True,
        help=':sun: :clock12: :triangular_ruler: NOAA\'s general solar position calculations',
)
# @debug_if_needed(app)
def noaa(
    ctx: typer.Context,
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = 1.5853349194640094,  # radians
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    verbose: Annotated[Optional[bool], typer_option_verbose]= False,
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
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
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

@app.command(
        'overview',
        no_args_is_help=True,
        help='⦩⦬ Calculate important solar position parameters',
 )
# @debug_if_needed(app)
def position(
    ctx: typer.Context,
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    model: Annotated[List[SolarPositionModels], typer_option_solar_position_model] = [SolarPositionModels.skyfield],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = 1.5853349194640094,  # radians
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365,  #365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    verbose: Annotated[Optional[bool], typer_option_verbose]= False,
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
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        models=model,  # could be named models!
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    print_solar_position_table(
        longitude,
        latitude,
        timestamp,
        timezone,
        solar_position,
        rounding_places,
        declination=True,
        altitude=True,
        azimuth=True,
        zenith=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
    )


@app.command('altitude', no_args_is_help=True, help='⦩ Calculate the solar altitude')
# @debug_if_needed(app)
def altitude(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    model: Annotated[List[SolarPositionModels], typer_option_solar_position_model] = [SolarPositionModels.skyfield],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    verbose: Annotated[Optional[bool], typer_option_verbose]= False,
) -> float:
    """Calculate the solar altitude angle above the horizon.

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
    solar_position = calculate_solar_altitude(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        models=model,  # could be named models!
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        solar_time_model=solar_time_model,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    print_solar_position_table(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_position=solar_altitude,
        rounding_places=rounding_places,
        altitude=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
    )


@app.command('zenith', no_args_is_help=True, help=' Calculate the solar zenith')
# @debug_if_needed(app)
def zenith(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    model: Annotated[List[SolarPositionModels], typer_option_solar_position_model] = [SolarPositionModels.skyfield],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    verbose: Annotated[Optional[bool], typer_option_verbose]= False,
) -> float:
    """Calculate the solar zenith angle

    The solar zenith angle (SZA) is the angle between the zenith (directly
    overhead) and the line to the sun. A zenith angle of 0 degrees means the
    sun is directly overhead, while an angle of 90 degrees means the sun is on
    the horizon.

    Parameters
    ----------

    Returns
    -------

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
    solar_altitude = calculate_solar_altitude(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        models=model,  # could be named models!
        solar_time_model=solar_time_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    for model_result in solar_altitude:
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
        solar_altitude,
        rounding_places,
        zenith=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
    )


@app.command('azimuth', no_args_is_help=True, help='⦬ Calculate the solar azimuth')
# @debug_if_needed(app)
def azimuth(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    model: Annotated[List[SolarPositionModels], typer_option_solar_position_model] = [SolarPositionModels.skyfield],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    verbose: Annotated[Optional[bool], typer_option_verbose]= False,
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
    solar_azimuth = calculate_solar_azimuth(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        models=model,  # could be named models!
        solar_time_model=solar_time_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    print_solar_position_table(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_position=solar_azimuth,
        rounding_places=rounding_places,
        azimuth=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
    )


@app.command('declination', no_args_is_help=True, help='∢ Calculate the solar declination')
def declination(
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    local_time: Annotated[bool, typer_option_local_time] = False,
    random_time: Annotated[bool, typer_option_random_time] = False,
    model: Annotated[List[SolarDeclinationModels], typer_option_solar_position_model] = [SolarDeclinationModels.pvis],
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    verbose: Annotated[Optional[bool], typer_option_verbose]= False,
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
    # Initialize with None ---------------------------------------------------
    user_requested_timestamp = None
    user_requested_timezone = None
    # -------------------------------------------- Smarter way to do this? ---

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

    # Why does the callback function `_parse_model` not work? ----------------
    if SolarDeclinationModels.all in model:
        model = [
            model for model in SolarDeclinationModels if model != SolarDeclinationModels.all
        ]
    solar_declination = calculate_solar_declination(
        timestamp=timestamp,
        timezone=timezone,
        models=model,
        days_in_a_year=days_in_a_year,
        eccentricity_correction_factor=eccentricity_correction_factor,
        perigee_offset=perigee_offset,
        angle_output_units=angle_output_units,
    )
    print_solar_position_table(
        longitude=None,
        latitude=None,
        timestamp=timestamp,
        timezone=timezone,
        solar_position=solar_declination,
        rounding_places=rounding_places,
        declination=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone,
        )


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
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    solar_incidence_model: Annotated[List[SolarIncidenceModels], typer_option_solar_incidence_model] = [SolarIncidenceModels.jenco],
    random_time: Annotated[bool, typer_option_random_time] = False,
    hour_angle: Annotated[Optional[float], typer_argument_hour_angle] = None,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = 45,
    random_surface_tilt: Annotated[Optional[bool], typer_option_random_surface_tilt] = False,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = 180,
    random_surface_orientation: Annotated[Optional[bool], typer_option_random_surface_orientation] = False,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    verbose: Annotated[Optional[bool], typer_option_verbose]= False,
):
    """Calculate the angle of solar incidence

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
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        random_time=random_time,
        hour_angle=hour_angle,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        days_in_a_year=days_in_a_year,
        eccentricity_correction_factor=eccentricity_correction_factor,
        perigee_offset=perigee_offset,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        rounding_places=rounding_places,
        verbose=verbose,
    )

    typer.echo(f'Solar incidence angle {solar_incidence_angle} {angle_output_units}')


@app.command(
    'incidence-effective',
    no_args_is_help=True,
    help='Calculate the effective solar incidence angle considering shadows',
)
def incidence_effective(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    solar_declination: Annotated[Optional[float], typer_argument_solar_declination] = 0,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = 0,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = 180,
    hour_angle: Annotated[Optional[float], typer_argument_hour_angle] = None,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
        ):
    """Calculate the angle of incidence

    The angle of incidence (also known as theta) is the angle between the
    direct beam of sunlight and the line perpendicular (normal) to the surface.
    If the sun is directly overhead and the surface is flat (horizontal), the
    angle of incidence is 0°.
    """
    effective_solar_incidence_angle = calculate_effective_solar_incidence_angle(
        longitude=longitude,
        latitude=latitude,
        hour_angle=hour_angle,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        solar_azimuth=solar_azimuth,
        solar_altitude=solar_altitude,
        shadow_indicator=shadow_indicator,
        horizon_heights=horizon_heights,
        horizon_interval=horizon_interval,
    )

    return effective_solar_incidence_angle


@app.command('hour-angle', no_args_is_help=True, help=':clock12: :globe_with_meridians: Calculate the hour angle (ω)')
def hour_angle(
    solar_time: Annotated[float, typer_argument_solar_time],
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
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
            solar_time=solar_time,
            angle_output_units=angle_output_units,
            )
    typer.echo(f'Hour angle: {hour_angle.value} {hour_angle.unit}')


@app.command('sunrise', no_args_is_help=True, help=':sunrise: Calculate the hour angle (ω) at sun rise and set')
def sunrise(
    latitude: Annotated[float, typer_argument_latitude],
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = 0,
    solar_declination: Annotated[Optional[float], typer_argument_solar_declination] = 0,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
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
            latitude,
            surface_tilt,
            solar_declination,
            angle_output_units=angle_output_units,
            )

    output_latitude = convert_to_degrees_if_requested(latitude, angle_output_units)
    typer.echo(f'Hour angle at {output_latitude} at sun rise/set: {hour_angle.value} {hour_angle.unit}')


if __name__ == "__main__":
    # import sys
    # commands = {'all', 'altitude', 'azimuth'}
    # sys.argv.insert(1, 'all') if sys.argv[1] not in commands else None
    # # debug(locals())
    app()
