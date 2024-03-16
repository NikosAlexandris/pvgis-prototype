from typing import Annotated
from typing import Optional
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_timestamp
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_verbose

from pvgisprototype.api.geometry.models import SolarPositionModel
from pvgisprototype.api.geometry.models import SolarTimeModel
from pvgisprototype.api.geometry.models import select_models

from pvgisprototype.constants import RADIANS, DEGREES
from pvgisprototype.constants import ZENITH_NAME
from pvgisprototype.constants import ALTITUDE_NAME
from pvgisprototype.constants import TIME_OFFSET_GLOBAL_DEFAULT
from pvgisprototype.constants import HOUR_OFFSET_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT

from math import radians
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.geometry.altitude import calculate_solar_altitude
from pvgisprototype.cli.print import print_solar_position_table


def calculate_zenith(angle_output_units, solar_altitude_angle):
    if angle_output_units == DEGREES:
        return 90 - solar_altitude_angle
    else:
        return radians(90) - radians(solar_altitude_angle)

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
        print(f'The requested timestamp - zone {user_requested_timestamp} {user_requested_timezone} has been converted to {timestamp} for all internal calculations!')

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
