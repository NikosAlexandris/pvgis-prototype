"""
CLI module to calculate the solar altitude angle parameters over a
location and a moment in time.
"""

from typing import Annotated, Sequence
from typing import Optional
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo

from pvgisprototype.api.position.altitude_series import calculate_solar_altitude_time_series
from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_random_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_periods
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.refraction import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.earth_orbit import typer_option_perigee_offset
from pvgisprototype.cli.typer.earth_orbit import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.output import typer_option_index

from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import select_models

from pvgisprototype.constants import RADIANS, DEGREES
from pvgisprototype.constants import ZENITH_NAME
from pvgisprototype.constants import ALTITUDE_NAME
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT

from math import radians
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pandas import DatetimeIndex
from pandas import Timestamp
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import RANDOM_TIMESTAMPS_FLAG_DEFAULT
from pvgisprototype import SolarAltitude


def altitude(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(now_utc_datetimezone()),
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,  # Used by a callback function
    periods: Annotated[Optional[int], typer_option_periods] = None,  # Used by a callback function
    frequency: Annotated[Optional[str], typer_option_frequency] = None,  # Used by a callback function
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,  # Used by a callback function
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_timestamps: Annotated[bool, typer_option_random_timestamps] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    model: Annotated[list[SolarPositionModel], typer_option_solar_position_model] = [SolarPositionModel.noaa],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.milne,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[int, typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    group_models: Annotated[Optional[bool], 'Visually cluster time series results per model'] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
) -> SolarAltitude:
    """Calculate the solar altitude angle above the horizon.

    The solar altitude angle (SAA) is the complement of the solar zenith angle,
    measuring from the horizon directly below the sun to the sun itself. An
    altitude of 0 degrees means the sun is on the horizon, and an altitude of
    90 degrees means the sun is directly overhead.

    Parameters
    ----------
    """
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

    solar_position_models = select_models(SolarPositionModel, model)  # Using a callback fails!
    from devtools import debug
    solar_altitude_series = calculate_solar_altitude_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_models=solar_position_models,
        solar_time_model=solar_time_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        # angle_output_units=angle_output_units,
        array_backend=array_backend,
        dtype=dtype,
        verbose=verbose,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    from pvgisprototype.cli.print import print_solar_position_series_table
    print_solar_position_series_table(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        table=solar_altitude_series,
        title='Solar Altitude Series',
        index=index,
        timing=True,
        declination=None,
        hour_angle=None,
        zenith=None,
        altitude=True,
        azimuth=None,
        surface_orientation=None,
        surface_tilt=None,
        incidence=None,
        user_requested_timestamps=user_requested_timestamps, 
        user_requested_timezone=user_requested_timezone,
        rounding_places=rounding_places,
        group_models=group_models,
    )
