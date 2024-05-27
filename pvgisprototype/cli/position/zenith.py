"""
CLI module to calculate the solar zenith angle for a location and a single moment in time.
"""

from pathlib import Path
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

from pvgisprototype.api.position.models import SolarPositionModel, SolarPositionParameter
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import select_models

from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT

from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.position.zenith import calculate_solar_zenith_series
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import RANDOM_TIMESTAMPS_FLAG_DEFAULT
from pvgisprototype import SolarAltitude
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.cli.typer.data_processing import typer_option_dtype
from pvgisprototype.cli.typer.data_processing import typer_option_array_backend
from pvgisprototype.cli.typer.plot import typer_option_uniplot
from pvgisprototype.cli.typer.plot import typer_option_uniplot_terminal_width
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.verbosity import typer_option_quiet
from pvgisprototype.cli.typer.output import typer_option_panels_output
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import CSV_PATH_DEFAULT, QUIET_FLAG_DEFAULT, TERMINAL_WIDTH_FRACTION, UNIPLOT_FLAG_DEFAULT
from pvgisprototype.constants import INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT
from pvgisprototype.cli.typer.output import typer_option_index

from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_random_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_periods
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from datetime import datetime


@log_function_call
def zenith(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(now_utc_datetimezone()),
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,  # Used by a callback function
    periods: Annotated[Optional[int], typer_option_periods] = None,  # Used by a callback function
    frequency: Annotated[Optional[str], typer_option_frequency] = None,  # Used by a callback function
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,  # Used by a callback function
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_timestamps: Annotated[bool, typer_option_random_timestamps] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    model: Annotated[List[SolarPositionModel], typer_option_solar_position_model] = [SolarPositionModel.noaa],
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.milne,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[int, typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    group_models: Annotated[Optional[bool], 'Visually cluster time series results per model'] = False,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, 'Resample large time series?'] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    panels: Annotated[bool, typer_option_panels_output] = False,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
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

        timestamps = timestamps.tz_localize(utc_zoneinfo)
        timezone = utc_zoneinfo
        logger.info(f'Input timestamps & zone ({user_requested_timestamps} & {user_requested_timezone}) converted to {timestamps} for all internal calculations!')

    solar_position_models = select_models(SolarPositionModel, model)  # Using a callback fails!
    solar_zenith_series = calculate_solar_zenith_series(
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
        array_backend=array_backend,
        dtype=dtype,
        verbose=verbose,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    if not quiet:
        from pvgisprototype.cli.print import print_solar_position_series_table
        print_solar_position_series_table(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            table=solar_zenith_series,
            position_parameters=[SolarPositionParameter.zenith],
            title='Solar Zenith Series',
            index=index,
            surface_orientation=None,
            surface_tilt=None,
            incidence=None,
            user_requested_timestamps=user_requested_timestamps, 
            user_requested_timezone=user_requested_timezone,
            rounding_places=rounding_places,
            group_models=group_models,
            panels=panels,
        )
    if csv:
        from pvgisprototype.cli.write import write_solar_position_series_csv
        write_solar_position_series_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            table=solar_zenith_series,
            # timing=True,
            # declination=True,
            # hour_angle=None,
            zenith=True,
            # altitude=None,
            # azimuth=None,
            # surface_orientation=None,
            # surface_tilt=None,
            # incidence=None,
            user_requested_timestamps=user_requested_timestamps, 
            user_requested_timezone=user_requested_timezone,
            # rounding_places=rounding_places,
            # group_models=group_models,
            filename=csv,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_solar_position_series
        uniplot_solar_position_series(
            solar_position_series=solar_zenith_series,
            position_parameters=[SolarPositionParameter.zenith],
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle='Solar Zenith Series',
            title="Solar Zenith",
            label='Zenith',
            legend_labels=None,
            terminal_width_fraction=terminal_width_fraction,
        )
