from devtools import debug
from pvgisprototype.cli.debug import debug_if_needed

"""
Important sun and solar surface geometry parameters in calculating the amount of solar radiation that reaches a particular location on the Earth's surface
"""

import typer
from rich import print
from typing import Annotated
from typing import Optional
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from math import radians
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_timestamp
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_frequency
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_local_time
from pvgisprototype.cli.typer_parameters import typer_option_random_time
from pvgisprototype.cli.typer_parameters import typer_argument_hour_angle
from pvgisprototype.cli.typer_parameters import typer_argument_true_solar_time
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_incidence_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.cli.typer_parameters import typer_option_index
from pvgisprototype.api.utilities.timestamp import random_datetimezone
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.geometry.hour_angle import calculate_event_hour_angle
from pvgisprototype.api.geometry.models import select_models
from pvgisprototype.api.geometry.models import SolarIncidenceModel
from pvgisprototype.api.geometry.models import SolarPositionModel
from pvgisprototype.api.geometry.models import SolarTimeModel
from pvgisprototype.api.geometry.overview import calculate_solar_geometry_overview
from pvgisprototype.api.geometry.overview_series import calculate_solar_geometry_overview_time_series
from pvgisprototype.algorithms.noaa.solar_position import calculate_noaa_solar_position
from pvgisprototype import SurfaceTilt
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
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
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_introduction
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_overview
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_position
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_geometry_noaa
from pvgisprototype.cli.print import print_solar_position_table
from pvgisprototype.cli.print import print_noaa_solar_position_table
from pvgisprototype.cli.write import write_solar_position_series_csv

from pvgisprototype.cli.position.introduction import introduction

from pvgisprototype.cli.position.overview import overview
from pvgisprototype.cli.position.overview_series import overview_series

from pvgisprototype.cli.position.declination import declination
from pvgisprototype.cli.position.hour_angle import hour_angle
from pvgisprototype.cli.position.sunrise import sunrise
from pvgisprototype.cli.position.zenith import zenith
from pvgisprototype.cli.position.altitude import altitude
from pvgisprototype.cli.position.azimuth import azimuth
from pvgisprototype.cli.position.incidence import incidence

# from pvgisprototype.cli.position.noaa import noaa


state = {"verbose": False}


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":triangular_ruler: Calculate solar geometry parameters for a location and moment in time",
)


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

app.command(
    name='introduction',
    help='A short primer on solar geometry',
    no_args_is_help=False,
    rich_help_panel=rich_help_panel_introduction,
)(introduction)
app.command(
    'overview',
    help='⦩⦬ Calculate solar position parameters',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_overview,
)(overview)
app.command(
    'overview-series',
    help='⦩⦬📈 Calculate series of solar position parameters',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_overview,
)(overview_series)
app.command(
    'declination',
    help='∢ Calculate the solar declination',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(declination)
app.command(
    'zenith',
    help=f' Calculate the solar zenith',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(zenith)
app.command(
    'hour-angle',
    help=':clock12: :globe_with_meridians: Calculate the hour angle (ω)',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(hour_angle)
app.command(
    'sun-rise-set',
     help=':sunrise: Calculate the hour angle (ω) at sun rise and set',
     no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(sunrise)
app.command(
    'altitude',
    help=f'⦩ Calculate the solar altitude',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(altitude)
app.command(
    'azimuth',
    help='⦬ Calculate the solar azimuth',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(azimuth)
app.command(
    'incidence',
    help=f'⭸ Calculate the solar incidence angle',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_solar_position,
)(incidence)
# app.command(
#     'noaa',
#     help=':sun: :clock12: :triangular_ruler: NOAA\'s general solar position calculations',
#     no_args_is_help=True,
#     rich_help_panel=rich_help_panel_geometry_noaa,
# )(noaa)


if __name__ == "__main__":
    # import sys
    # commands = {'all', 'altitude', 'azimuth'}
    # sys.argv.insert(1, 'all') if sys.argv[1] not in commands else None
    app()
