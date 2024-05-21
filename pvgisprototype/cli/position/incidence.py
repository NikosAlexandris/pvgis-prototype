"""
CLI module to calculate the solar incidence angle for a solar surface at a
location, orientation, tilt and moment in time.
"""

from typing import Annotated
from typing import Optional
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

from click.utils import R

from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.timestamps import typer_option_random_time
from pvgisprototype.cli.typer.timing import typer_argument_hour_angle
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamp
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.refraction import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.earth_orbit import typer_option_perigee_offset
from pvgisprototype.cli.typer.earth_orbit import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer.position import typer_option_solar_incidence_model
from pvgisprototype.cli.typer.position import typer_argument_surface_orientation
from pvgisprototype.cli.typer.position import typer_option_random_surface_orientation
from pvgisprototype.cli.typer.position import typer_argument_surface_tilt
from pvgisprototype.cli.typer.position import typer_option_random_surface_tilt
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.verbosity import typer_option_verbose

from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import select_models

from pvgisprototype.constants import RADIANS, RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.constants import COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT

from math import pi
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.timestamp import random_datetimezone
from pvgisprototype.api.position.incidence import calculate_solar_incidence_series
from pvgisprototype.cli.print import print_solar_position_table
from pvgisprototype import SurfaceOrientation
from pvgisprototype import SurfaceTilt


def incidence(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    random_surface_orientation: Annotated[Optional[bool], typer_option_random_surface_orientation] = False,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    random_surface_tilt: Annotated[Optional[bool], typer_option_random_surface_tilt] = False,
    solar_incidence_model: Annotated[List[SolarIncidenceModel], typer_option_solar_incidence_model] = [SolarIncidenceModel.iqbal],
    complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    random_time: Annotated[bool, typer_option_random_time] = RANDOM_DAY_FLAG_DEFAULT,
    hour_angle: Annotated[Optional[float], typer_argument_hour_angle] = None,
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
        print(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')

    # --------------------------------------------------------------- Idea ---
    # if not given, optimise tilt and orientation... ?
    # ------------------------------------------------------------------------

    if random_surface_orientation:
        import random
        surface_tilt = random.vonmisesvariate(pi, kappa=0)  # radians

    if random_surface_tilt:
        import random
        surface_tilt = random.uniform(0, pi/2)  # radians

    solar_incidence_models = select_models(SolarIncidenceModel, solar_incidence_model)  # Using a callback fails!
    solar_incidence = calculate_solar_incidence_series(
        # longitude=longitude,
        # latitude=latitude,
        # timestamps=timestamp,
        # timezone=timezone,
        # solar_incidence_models=solar_incidence_models,
        # complementary_incidence_angle=complementary_incidence_angle,
        # surface_orientation=SurfaceOrientation(value=surface_orientation, unit=RADIANS),  # Typer does not easily support custom types !
        # surface_tilt=SurfaceTilt(value=surface_tilt, unit=RADIANS),  # Typer does not easily support custom types !
        # solar_time_model=solar_time_model,
        # eccentricity_correction_factor=eccentricity_correction_factor,
        # perigee_offset=perigee_offset,
        # angle_output_units=angle_output_units,
        # verbose=verbose,
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

