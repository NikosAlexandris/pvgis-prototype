"""
CLI module for an overview of solar position parameters for a location and a single moment in time.
"""

from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
import typer
from click import Context
from typing import Annotated
from typing import Optional
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from rich import print
from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamp
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.position import typer_argument_surface_orientation
from pvgisprototype.cli.typer.position import typer_option_random_surface_orientation
from pvgisprototype.cli.typer.position import typer_argument_surface_tilt
from pvgisprototype.cli.typer.position import typer_option_random_surface_tilt
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.position import typer_option_solar_incidence_model
from pvgisprototype.cli.typer.refraction import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer.refraction import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.earth_orbit import typer_option_perigee_offset
from pvgisprototype.cli.typer.earth_orbit import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.output import typer_option_panels_output

from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.position.models import select_models
from pvgisprototype.api.position.overview import calculate_solar_geometry_overview
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.cli.print import print_solar_position_table

from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone


def overview(
    ctx: typer.Context,
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    random_surface_orientation: Annotated[Optional[bool], typer_option_random_surface_orientation] = False,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    random_surface_tilt: Annotated[Optional[bool], typer_option_random_surface_tilt] = False,
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp] = str(now_utc_datetimezone()),
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    model: Annotated[List[SolarPositionModel], typer_option_solar_position_model] = [SolarPositionModel.pvlib],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.milne,
    solar_incidence_model: Annotated[SolarIncidenceModel, typer_option_solar_incidence_model] = SolarIncidenceModel.iqbal,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    panels: Annotated[bool, typer_option_panels_output] = False,
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
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        solar_position_models=solar_position_models,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        solar_time_model=solar_time_model,
        solar_incidence_model=solar_incidence_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    if not panels:
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
            surface_orientation=True,
            surface_tilt=True,
            incidence=True,  # Add Me ?
            user_requested_timestamp=user_requested_timestamp, 
            user_requested_timezone=user_requested_timezone
        )
    else:
        from pvgisprototype.cli.print import print_solar_position_table_panels
        print_solar_position_table_panels(
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

