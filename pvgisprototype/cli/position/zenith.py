"""
CLI module to calculate the solar zenith angle for a location and a single moment in time.
"""

from typing import Annotated
from typing import Optional
from typing import List
from zoneinfo import ZoneInfo

from pandas import DatetimeIndex

from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.refraction import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.earth_orbit import typer_option_perigee_offset
from pvgisprototype.cli.typer.earth_orbit import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.verbosity import typer_option_verbose

from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import select_models

from pvgisprototype.constants import DEGREES
from pvgisprototype.constants import ZENITH_NAME
from pvgisprototype.constants import ALTITUDE_NAME
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT

from math import radians
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.position.altitude import calculate_solar_altitude_time_series
from pvgisprototype.cli.print import print_solar_position_table


def calculate_zenith(angle_output_units, solar_altitude_angle):
    if angle_output_units == DEGREES:
        return 90 - solar_altitude_angle
    else:
        return radians(90) - radians(solar_altitude_angle)


def zenith(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(now_utc_datetimezone()),
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    model: Annotated[List[SolarPositionModel], typer_option_solar_position_model] = [SolarPositionModel.skyfield],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.milne,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
) -> None:
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
    user_requested_timestamps = None
    user_requested_timezone = None
    # -------------------------------------------- Smarter way to do this? ---

    # Convert the input timestamp to UTC, for _all_ internal calculations
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamps.tz != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamps = timestamps
        user_requested_timezone = timezone

        timestamps = timestamps.tz_convert(utc_zoneinfo)
        print(f'The requested timestamp - zone {user_requested_timestamps} {user_requested_timezone} has been converted to {timestamps} for all internal calculations!')

    solar_position_models = select_models(SolarPositionModel, model)  # Using a callback fails!
    solar_altitude = calculate_solar_altitude_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
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
    for _, model_result in solar_zenith.items():
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
        timestamp=timestamps,
        timezone=timezone,
        table=solar_zenith,
        rounding_places=rounding_places,
        declination=None,
        hour_angle=None,
        timing=True,
        zenith=True,
        altitude=None,
        azimuth=None,
        surface_orientation=None,
        surface_tilt=None,
        incidence=None,
        user_requested_timestamp=user_requested_timestamps,
        user_requested_timezone=user_requested_timezone,
    )
