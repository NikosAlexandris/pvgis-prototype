"""
CLI module to calculate the solar declination angle for a location and moment in time.
"""

from rich import print
from typing import Annotated
from typing import Optional
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

from pvgisprototype.api.position.models import SolarDeclinationModel
from pvgisprototype.api.position.models import select_models

from pvgisprototype.cli.typer.timestamps import typer_argument_timestamp
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.timestamps import typer_option_local_time
from pvgisprototype.cli.typer.timestamps import typer_option_random_time
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.refraction import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.earth_orbit import typer_option_perigee_offset
from pvgisprototype.cli.typer.earth_orbit import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.verbosity import typer_option_verbose

from pvgisprototype.api.utilities.timestamp import random_datetimezone
from pvgisprototype.api.position.declination import calculate_solar_declination_series
from pvgisprototype.cli.print import print_solar_position_table

from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT


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
    """Calculate the solar declination angle 

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
        print(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')

    solar_declination_models = select_models(SolarDeclinationModel, model)  # Using a callback fails!
    solar_declination = calculate_solar_declination_series(
        # timestamps=timestamp,
        # timezone=timezone,
        # declination_models=solar_declination_models,
        # eccentricity_correction_factor=eccentricity_correction_factor,
        # perigee_offset=perigee_offset,
        # angle_output_units=angle_output_units,
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
