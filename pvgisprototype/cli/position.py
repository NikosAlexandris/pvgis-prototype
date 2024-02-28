from devtools import debug
from pvgisprototype.cli.debug import debug_if_needed

"""
Important sun and solar surface geometry parameters in calculating the amount of solar radiation that reaches a particular location on the Earth's surface
"""

import typer
from click import Context
from typing import Annotated
from typing import Optional
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import math
from math import radians
from rich import print
from .typer_parameters import OrderCommands
from .typer_parameters import typer_argument_longitude
from .typer_parameters import typer_argument_latitude
from .typer_parameters import typer_argument_timestamp
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_frequency
from pvgisprototype.cli.typer_parameters import typer_option_end_time
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
from .typer_parameters import typer_option_perigee_offset
from .typer_parameters import typer_option_eccentricity_correction_factor
from .typer_parameters import typer_option_apply_atmospheric_refraction
from .typer_parameters import typer_option_refracted_solar_zenith
from .typer_parameters import typer_option_time_output_units
from .typer_parameters import typer_option_angle_units
from .typer_parameters import typer_option_angle_output_units
from .typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.cli.typer_parameters import typer_option_csv
from .typer_parameters import typer_option_verbose
from pvgisprototype.cli.typer_parameters import typer_option_index
from pvgisprototype.api.utilities.timestamp import random_datetimezone
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.geometry.declination import calculate_solar_declination
from pvgisprototype.api.geometry.incidence import calculate_solar_incidence
from pvgisprototype.api.geometry.hour_angle import calculate_solar_hour_angle
from pvgisprototype.api.geometry.hour_angle import calculate_event_hour_angle
from pvgisprototype.api.geometry.altitude import calculate_solar_altitude
from pvgisprototype.api.geometry.azimuth import calculate_solar_azimuth
from pvgisprototype.api.geometry.models import select_models
from pvgisprototype.api.geometry.models import SolarDeclinationModel
from pvgisprototype.api.geometry.models import SolarIncidenceModel
from pvgisprototype.api.geometry.models import SolarPositionModel
from pvgisprototype.api.geometry.models import SolarTimeModel
from pvgisprototype.api.geometry.overview import calculate_solar_geometry_overview
from pvgisprototype.api.geometry.overview_series import calculate_solar_geometry_overview_time_series
from pvgisprototype.algorithms.noaa.solar_position import calculate_noaa_solar_position
from pvgisprototype import Latitude
from pvgisprototype import SurfaceTilt
from pvgisprototype import SolarDeclination
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import TIME_OFFSET_GLOBAL_DEFAULT
from pvgisprototype.constants import HOUR_OFFSET_DEFAULT
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import ZENITH_NAME
from pvgisprototype.constants import ALTITUDE_NAME
from pvgisprototype.constants import RADIANS, DEGREES
from pvgisprototype.cli.documentation import A_PRIMER_ON_SOLAR_GEOMETRY
from .rich_help_panel_names import rich_help_panel_geometry_noaa
from .print import print_solar_position_table
from .print import print_noaa_solar_position_table
from pvgisprototype.cli.write import write_solar_position_series_csv


def calculate_zenith(angle_output_units, solar_altitude_angle):
    if angle_output_units == DEGREES:
        return 90 - solar_altitude_angle
    else:
        return radians(90) - radians(solar_altitude_angle)


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
    verbose: Annotated[Optional[int], typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    debug: Annotated[Optional[bool], typer.Option(
        "--debug",
        help="Enable debug mode")] = False,
):
    """
    Solar position algorithms
    """
    # if verbose > 2:
    #     print(f"Executing command: {ctx.invoked_subcommand}")
    if verbose > 0:
        print("Will output verbosely")
        # state["verbose"] = True

    app.debug_mode = debug


@app.command(
    'intro',
    no_args_is_help=False,
    help='A short primer on solar geometry',
 )
# @debug_if_needed(app)
def intro():
    """A short introduction on solar geometry"""
    introduction = """
    [underline]Solar geometry[/underline] consists of a series of angular
    measurements between the position of the sun in the sky and a location on
    the surface of the earth for a moment or series of moments in time.
    """

    note = """
    Internally,
        - [bold]timestamps[/bold] are converted to [magenta]UTC[/magenta]
        - angles are measured in radians!
    """
    from rich.panel import Panel
    note_in_a_panel = Panel(
        "[italic]{}[/italic]".format(note),
        title="[bold cyan]Note[/bold cyan]",
        width=78,
    )
    from rich.console import Console
    console = Console()
    # introduction.wrap(console, 30)
    console.print(introduction)
    console.print(note_in_a_panel)
    console.print(A_PRIMER_ON_SOLAR_GEOMETRY)


@app.command(
    'overview',
    no_args_is_help=True,
    help='⦩⦬ Calculate solar position parameters',
 )
# @debug_if_needed(app)
def overview(
    ctx: typer.Context,
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    random_surface_tilt: Annotated[Optional[bool], typer_option_random_surface_tilt] = False,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    random_surface_orientation: Annotated[Optional[bool], typer_option_random_surface_orientation] = False,
    model: Annotated[List[SolarPositionModel], typer_option_solar_position_model] = [SolarPositionModel.pvlib],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.milne,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: Annotated[float, typer_option_hour_offset] = HOUR_OFFSET_DEFAULT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
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
    
    solar_position_models = select_models(SolarPositionModel, model)  # Using a callback fails!
    solar_position = calculate_solar_geometry_overview(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        solar_position_models=solar_position_models,  # could be named models!
        solar_time_model=solar_time_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
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
        timing=True,
        declination=True,
        hour_angle=True,
        zenith=True,
        altitude=True,
        azimuth=True,
        incidence=False,  # Add Me ?
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
    )


DEFAULT_ARRAY_BACKEND = 'NUMPY'  # OR 'CUPY', 'DASK'
DEFAULT_ARRAY_DTYPE = 'float32'


@app.command(
    'overview-series',
    no_args_is_help=True,
    help='⦩⦬📈 Calculate series of solar position parameters',
 )
# @debug_if_needed(app)
def overview_series(
    ctx: typer.Context,
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamps: Annotated[Optional[datetime], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_time_series: bool = False,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    random_surface_tilt: Annotated[Optional[bool], typer_option_random_surface_tilt] = False,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    random_surface_orientation: Annotated[Optional[bool], typer_option_random_surface_orientation] = False,
    model: Annotated[List[SolarPositionModel], typer_option_solar_position_model] = [SolarPositionModel.noaa],
    complementary_incidence_angle: Annotated[bool, 'Measure angle between sun-vector and surface-plane'] = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.milne,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: Annotated[float, typer_option_hour_offset] = HOUR_OFFSET_DEFAULT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    group_models: Annotated[Optional[bool], 'Visually cluster time series results per model'] = False,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    dtype: str = DEFAULT_ARRAY_DTYPE,
    backend: str = DEFAULT_ARRAY_BACKEND,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = False,
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
    user_requested_timestamps = None
    user_requested_timezone = None
    # -------------------------------------------- Smarter way to do this? ---
    
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamps.tzinfo != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamps = timestamps
        user_requested_timezone = timezone

        # timestamps = timestamps.tz_convert(utc_zoneinfo)
        from pvgisprototype.api.utilities.timestamp import attach_requested_timezone
        timezone_aware_timestamps = [
            attach_requested_timezone(timestamp, timezone) for timestamp in timestamps
        ]
        timezone = utc_zoneinfo
        # print(f'Input timestamps & zone ({user_requested_timestamps} & {user_requested_timezone}) converted to {timestamps} for all internal calculations!')

    # Why does the callback function `_parse_model` not work? 
    solar_position_models = select_models(SolarPositionModel, model)  # Using a callback fails!
    solar_position_series = calculate_solar_geometry_overview_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        solar_position_models=solar_position_models,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        # refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        # time_offset_global=time_offset_global,
        # hour_offset=hour_offset,
        # time_output_units=time_output_units,
        # angle_units=angle_units,
        angle_output_units=angle_output_units,
        backend=backend,
        dtype=dtype,
        complementary_incidence_angle=complementary_incidence_angle,
        verbose=verbose,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    from pvgisprototype.cli.print import print_solar_position_series_table
    if not csv:
        print_solar_position_series_table(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            table=solar_position_series,
            timing=True,
            declination=True,
            hour_angle=True,
            zenith=True,
            altitude=True,
            azimuth=True,
            surface_tilt=True,
            surface_orientation=True,
            incidence=True,
            user_requested_timestamps=user_requested_timestamps, 
            user_requested_timezone=user_requested_timezone,
            rounding_places=rounding_places,
            group_models=group_models,
        )
    if csv:
        write_solar_position_series_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            table=solar_position_series,
            timing=True,
            declination=True,
            hour_angle=True,
            zenith=True,
            altitude=True,
            azimuth=True,
            surface_tilt=True,
            surface_orientation=True,
            incidence=True,
            user_requested_timestamps=user_requested_timestamps, 
            user_requested_timezone=user_requested_timezone,
            # rounding_places=rounding_places,
            # group_models=group_models,
            filename=csv,
        )


@app.command('declination', no_args_is_help=True, help='∢ Calculate the solar declination')
def declination(
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    local_time: Annotated[bool, typer_option_local_time] = False,
    random_time: Annotated[bool, typer_option_random_time] = False,
    model: Annotated[List[SolarDeclinationModel], typer_option_solar_position_model] = [SolarDeclinationModel.pvis],
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
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

    solar_declination_models = select_models(SolarDeclinationModel, model)  # Using a callback fails!
    solar_declination = calculate_solar_declination(
        timestamp=timestamp,
        timezone=timezone,
        declination_models=solar_declination_models,
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
    model: Annotated[List[SolarPositionModel], typer_option_solar_position_model] = [SolarPositionModel.skyfield],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.milne,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: Annotated[float, typer_option_hour_offset] = HOUR_OFFSET_DEFAULT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
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

    solar_position_models = select_models(SolarPositionModel, model)  # Using a callback fails!
    solar_altitude = calculate_solar_altitude(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_position_models=solar_position_models,
        solar_time_model=solar_time_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )
    solar_zenith = solar_altitude
    for model_result in solar_zenith:
        if ZENITH_NAME not in model_result:
            solar_altitude_angle = model_result.get(ALTITUDE_NAME, None)
            if solar_altitude_angle is not None:
                model_result[ZENITH_NAME] = calculate_zenith(
                    angle_output_units, solar_altitude_angle
                )

    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    print_solar_position_table(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        table=solar_zenith,
        rounding_places=rounding_places,
        timing=True,
        zenith=True,
        user_requested_timestamp=user_requested_timestamp,
        user_requested_timezone=user_requested_timezone,
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
    model: Annotated[List[SolarPositionModel], typer_option_solar_position_model] = [SolarPositionModel.skyfield],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.milne,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: Annotated[float, typer_option_hour_offset] = HOUR_OFFSET_DEFAULT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
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

    solar_position_models = select_models(SolarPositionModel, model)  # Using a callback fails!
    solar_altitude = calculate_solar_altitude(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_position_models=solar_position_models,
        solar_time_model=solar_time_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
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
        timing=True,
        altitude=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
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
    model: Annotated[List[SolarPositionModel], typer_option_solar_position_model] = [SolarPositionModel.skyfield],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.milne,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: Annotated[float, typer_option_hour_offset] = HOUR_OFFSET_DEFAULT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
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

    solar_position_models = select_models(SolarPositionModel, model)  # Using a callback fails!
    solar_azimuth = calculate_solar_azimuth(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_position_models=solar_position_models,
        solar_time_model=solar_time_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
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
        timing=True,
        azimuth=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
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

    hour_angle = calculate_solar_hour_angle(
        solar_time=solar_time,
    )
    from pvgisprototype.cli.print import print_hour_angle_table_2
    print_hour_angle_table_2(
        solar_time=solar_time,
        rounding_places=rounding_places,
        hour_angle=getattr(hour_angle, angle_output_units),
        units=angle_output_units,
    )
    print(f'Hour angle: {getattr(hour_angle, angle_output_units)} {angle_output_units}')


@app.command('sunrise', no_args_is_help=True, help=':sunrise: Calculate the hour angle (ω) at sun rise and set')
def sunrise(
    latitude: Annotated[float, typer_argument_latitude],
    solar_declination: Annotated[Optional[float], typer_argument_solar_declination] = 45,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
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
    latitude = Latitude(value=latitude, unit=RADIANS)
    hour_angle = calculate_event_hour_angle(
        latitude=latitude,
        surface_tilt=surface_tilt,
        solar_declination=solar_declination,
    )
    surface_tilt = SurfaceTilt(value=surface_tilt, unit=RADIANS)
    solar_declination = SolarDeclination(value=solar_declination, unit=RADIANS)

    from pvgisprototype.cli.print import print_hour_angle_table
    print_hour_angle_table(
            latitude=getattr(latitude, angle_output_units),
            rounding_places=rounding_places,
            surface_tilt=getattr(surface_tilt, angle_output_units),
            declination=getattr(solar_declination, angle_output_units),
            hour_angle=getattr(hour_angle, angle_output_units),
            units=angle_output_units,
    )


@app.command(
    'incidence',
    no_args_is_help=True,
    help=f'⭸ Calculate the solar incidence angle',
)
def incidence(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    solar_incidence_model: Annotated[List[SolarIncidenceModel], typer_option_solar_incidence_model] = [SolarIncidenceModel.jenco],
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    random_time: Annotated[bool, typer_option_random_time] = RANDOM_DAY_FLAG_DEFAULT,
    hour_angle: Annotated[Optional[float], typer_argument_hour_angle] = None,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    random_surface_tilt: Annotated[Optional[bool], typer_option_random_surface_tilt] = False,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    random_surface_orientation: Annotated[Optional[bool], typer_option_random_surface_orientation] = False,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.milne,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
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

    # --------------------------------------------------------------- Idea ---
    # if not given, optimise tilt and orientation... ?
    # ------------------------------------------------------------------------

    if random_surface_tilt:
        import random
        surface_tilt = random.uniform(0, math.pi/2)  # radians

    if random_surface_orientation:
        import random
        surface_tilt = random.vonmisesvariate(math.pi, kappa=0)  # radians

    solar_incidence_models = select_models(SolarIncidenceModel, solar_incidence_model)  # Using a callback fails!
    solar_incidence = calculate_solar_incidence(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_incidence_models=solar_incidence_models,
        complementary_incidence_angle=complementary_incidence_angle,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        solar_time_model=solar_time_model,
        eccentricity_correction_factor=eccentricity_correction_factor,
        perigee_offset=perigee_offset,
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
        timing=True,
        incidence=True,
        user_requested_timestamp=user_requested_timestamp, 
        user_requested_timezone=user_requested_timezone
    )


@app.command(
    no_args_is_help=True,
    help=':sun: :clock12: :triangular_ruler: NOAA\'s general solar position calculations',
    rich_help_panel=rich_help_panel_geometry_noaa,
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
    angle_units: Annotated[str, typer_option_angle_units] = RADIANS,
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


if __name__ == "__main__":
    # import sys
    # commands = {'all', 'altitude', 'azimuth'}
    # sys.argv.insert(1, 'all') if sys.argv[1] not in commands else None
    app()
