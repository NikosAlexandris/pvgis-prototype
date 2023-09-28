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
from .typer_parameters import typer_option_random_surface_tilt
from .typer_parameters import typer_argument_surface_orientation
from .typer_parameters import typer_option_random_surface_orientation
from .typer_parameters import typer_argument_hour_angle
from .typer_parameters import typer_argument_true_solar_time
from .typer_parameters import typer_option_solar_position_model
from .typer_parameters import typer_option_solar_incidence_model
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
from ..api.geometry.solar_incidence import calculate_solar_incidence
from pvgisprototype.algorithms.pyephem.solar_time import calculate_solar_time_ephem
from ..api.geometry.solar_hour_angle import calculate_hour_angle
from ..api.geometry.solar_hour_angle import calculate_hour_angle_sunrise
from ..api.geometry.solar_altitude import calculate_solar_altitude
from ..api.geometry.solar_azimuth import calculate_solar_azimuth
from ..api.geometry.models import SolarDeclinationModels
from ..api.geometry.models import SolarIncidenceModels
from ..api.geometry.models import SolarPositionModels
from ..api.geometry.models import SolarTimeModels
# from ..api.geometry.solar_position import _parse_model
from ..api.geometry.solar_position import calculate_solar_geometry_overview
from pvgisprototype.algorithms.noaa.solar_position import calculate_noaa_solar_position
from pvgisprototype import Latitude
from pvgisprototype import SurfaceTilt
from pvgisprototype import SolarDeclination
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import DAYS_IN_A_YEAR
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import TIME_OFFSET_GLOBAL_DEFAULT
from pvgisprototype.constants import HOUR_OFFSET_DEFAULT
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT

from .print import print_table
from .print import print_solar_position_table
from .print import print_noaa_solar_position_table


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":triangular_ruler: Calculate solar geometry parameters for a location and moment in time",
)
state = {"verbose": False}


@app.callback()
def main(
    ctx: typer.Context,
    verbose: Annotated[Optional[int], typer_option_verbose] = 0,
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
        # state["verbose"] = True

    app.debug_mode = debug


@app.command(
    'overview',
    no_args_is_help=True,
    help='⦩⦬ Calculate important solar position parameters',
 )
# @debug_if_needed(app)
def overview(
    ctx: typer.Context,
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    model: Annotated[List[SolarPositionModels], typer_option_solar_position_model] = [SolarPositionModels.pvlib],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: Annotated[float, typer_option_hour_offset] = HOUR_OFFSET_DEFAULT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = TIME_OUTPUT_UNITS_DEFAULT,
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
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
    
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamp.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamp = timestamp
        user_requested_timezone = timezone

        timestamp = timestamp.astimezone(utc_zoneinfo)
        timezone = utc_zoneinfo
        typer.echo(f'Input timestamp & zone ({user_requested_timestamp} & {user_requested_timezone}) converted to {timestamp} for all internal calculations!')
    
    # Why does the callback function `_parse_model` not work? 
    if SolarPositionModels.all in model:
        model = [model for model in SolarPositionModels if model != SolarPositionModels.all]

    solar_position = calculate_solar_geometry_overview(
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
        verbose=verbose,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    print_solar_position_table(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        table=solar_position,
        rounding_places=rounding_places,
        declination=True,
        hour_angle=True,
        zenith=True,
        altitude=True,
        azimuth=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
    )


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
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    time_output_units: Annotated[str, typer_option_time_output_units] = TIME_OUTPUT_UNITS_DEFAULT,
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
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
        typer.echo(f'Input timestamp & zone ({user_requested_timestamp} & {user_requested_timezone}) converted to {timestamp} for all internal calculations!')

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
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_position_calculations=solar_position_calculations, 
        rounding_places=rounding_places,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )


@app.command(
    'altitude',
    no_args_is_help=True,
    help=f'⦩ Calculate the solar altitude',
)
# @debug_if_needed(app)
def altitude(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    model: Annotated[List[SolarPositionModels], typer_option_solar_position_model] = [SolarPositionModels.skyfield],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: Annotated[float, typer_option_hour_offset] = HOUR_OFFSET_DEFAULT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = TIME_OUTPUT_UNITS_DEFAULT,
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
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
    solar_altitude = calculate_solar_altitude(
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
        verbose=verbose,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    print_solar_position_table(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        table=solar_altitude,
        rounding_places=rounding_places,
        altitude=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
    )


@app.command(
    'zenith',
    no_args_is_help=True,
    help=f' Calculate the solar zenith',
)
# @debug_if_needed(app)
def zenith(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    model: Annotated[List[SolarPositionModels], typer_option_solar_position_model] = [SolarPositionModels.skyfield],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: Annotated[float, typer_option_hour_offset] = HOUR_OFFSET_DEFAULT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = TIME_OUTPUT_UNITS_DEFAULT,
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
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

    # Update Me --- Zenith Comes First, Altitude Bases On It ! ---------------
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
        verbose=verbose,
    )

    def calculate_zenith(angle_output_units, solar_altitude_angle):
        if angle_output_units == 'degrees':
            return 90 - solar_altitude_angle
        else:
            return radians(90) - radians(solar_altitude_angle)

    solar_zenith = solar_altitude
    for model_result in solar_zenith:
        if 'Zenith' not in model_result:
            solar_altitude_angle = model_result.get('Altitude', None)
            if solar_altitude_angle is not None:
                model_result['Zenith'] = calculate_zenith(angle_output_units, solar_altitude_angle)

    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    print_solar_position_table(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        table=solar_zenith,
        rounding_places=rounding_places,
        zenith=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone,
    )


@app.command(
    'azimuth',
    no_args_is_help=True,
    help='⦬ Calculate the solar azimuth',
)
# @debug_if_needed(app)
def azimuth(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    model: Annotated[List[SolarPositionModels], typer_option_solar_position_model] = [SolarPositionModels.skyfield],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: Annotated[float, typer_option_hour_offset] = HOUR_OFFSET_DEFAULT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = TIME_OUTPUT_UNITS_DEFAULT,
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
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
        verbose=verbose,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    print_solar_position_table(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        table=solar_azimuth,
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
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
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
        table=solar_declination,
        rounding_places=rounding_places,
        declination=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone,
    )


@app.command('hour-angle', no_args_is_help=True, help=':clock12: :globe_with_meridians: Calculate the hour angle (ω)')
def hour_angle(
    solar_time: Annotated[float, typer_argument_true_solar_time],
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
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
    hour_angle = convert_to_degrees_if_requested(hour_angle, angle_output_units)
    from pvgisprototype.cli.print import print_hour_angle_table_2
    print_hour_angle_table_2(
        solar_time=solar_time,
        rounding_places=rounding_places,
        hour_angle=hour_angle.value,
        units=hour_angle.unit,
    )


@app.command('sunrise', no_args_is_help=True, help=':sunrise: Calculate the hour angle (ω) at sun rise and set')
def sunrise(
    latitude: Annotated[float, typer_argument_latitude],
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = 45,
    solar_declination: Annotated[Optional[float], typer_argument_solar_declination] = 45,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the hour angle 'ω = (ST / 3600 - 12) * 15 * π / 180'

    The hour angle (ω) is the angle at any instant through which the earth has
    to turn to bring the meridian of the observer directly in line with the
    sun's rays measured in radian. In other words, it is a measure of time,
    expressed in angular measurement, usually degrees, from solar noon. It
    increases by 15° per hour, negative before solar noon and positive after
    solar noon.
    """
    from rich.console import Console
    from rich.table import Table
    from rich import box


    #
    # Update Me
    #

    latitude = Latitude(value=latitude, unit='radians')
    output_latitude = convert_to_degrees_if_requested(latitude, angle_output_units)

    hour_angle = calculate_hour_angle_sunrise(
            latitude,
            surface_tilt,
            solar_declination,
            angle_output_units=angle_output_units,
            )
    output_hour_angle = convert_to_degrees_if_requested(hour_angle, angle_output_units)
    
    surface_tilt = SurfaceTilt(value=surface_tilt, unit='radians')
    output_surface_tilt = convert_to_degrees_if_requested(surface_tilt, angle_output_units)

    solar_declination = SolarDeclination(value=solar_declination, unit='radians')
    output_solar_declination = convert_to_degrees_if_requested(solar_declination, angle_output_units)

    typer.echo(f'Hour angle at {output_latitude} {latitude.unit} latitude at sun rise/set: {hour_angle.value} {hour_angle.unit}')

    from pvgisprototype.cli.print import print_hour_angle_table
    print_hour_angle_table(
            latitude=output_latitude.value,
            rounding_places=rounding_places,
            surface_tilt=output_surface_tilt.value,
            declination=output_solar_declination.value,
            hour_angle=hour_angle.value,
            units=angle_output_units,
    )


@app.command('incidence', no_args_is_help=True, help='Calculate the solar incidence angle')
def incidence(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    solar_incidence_model: Annotated[List[SolarIncidenceModels], typer_option_solar_incidence_model] = [SolarIncidenceModels.jenco],
    random_time: Annotated[bool, typer_option_random_time] = RANDOM_DAY_FLAG_DEFAULT,
    hour_angle: Annotated[Optional[float], typer_argument_hour_angle] = None,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    random_surface_tilt: Annotated[Optional[bool], typer_option_random_surface_tilt] = False,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    random_surface_orientation: Annotated[Optional[bool], typer_option_random_surface_orientation] = False,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = TIME_OUTPUT_UNITS_DEFAULT,
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the angle of solar incidence

    The angle of incidence (also known as theta) is the angle between the
    direct beam of sunlight and the line perpendicular (normal) to the surface.
    If the sun is directly overhead and the surface is flat (horizontal), the
    angle of incidence is 0°.
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

    # --------------------------------------------------------------- Idea ---
    # if not given, optimise tilt and orientation... ?
    # ------------------------------------------------------------------------

    if random_surface_tilt:
        import random
        surface_tilt = random.uniform(0, math.pi/2)  # radians

    if random_surface_orientation:
        import random
        surface_tilt = random.vonmisesvariate(math.pi, kappa=0)  # radians

    # Why does the callback function `_parse_model` not work? ----------------
    if SolarPositionModels.all in solar_incidence_model:
        solar_incidence_model = [
            model for model in SolarPositionModels if solar_incidence_model != SolarPositionModels.all
        ]
    solar_incidence = calculate_solar_incidence(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_incidence_models=solar_incidence_model,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        # shadow_indicator=shadow_indicator,
        # horizon_heights=horizon_heights,
        # horizon_interval=horizon_interval,
        days_in_a_year=days_in_a_year,
        eccentricity_correction_factor=eccentricity_correction_factor,
        perigee_offset=perigee_offset,
        random_time=random_time,
        # time_offset_global=time_offset_global,
        # hour_offset=hour_offset,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    print_solar_position_table(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        table=solar_incidence,
        rounding_places=rounding_places,
        incidence=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
    )


if __name__ == "__main__":
    # import sys
    # commands = {'all', 'altitude', 'azimuth'}
    # sys.argv.insert(1, 'all') if sys.argv[1] not in commands else None
    app()
