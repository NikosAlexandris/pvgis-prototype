from zoneinfo import ZoneInfo
from rich import print
from typing import Annotated, List
from typing import Optional

from pvgisprototype.api.position.models import SolarPositionModel, SolarPositionParameter, SolarTimeModel, select_models
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.cli.typer.timing import typer_argument_true_solar_time
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.verbosity import typer_option_verbose

from pvgisprototype.api.position.hour_angle import calculate_solar_hour_angle_series
from pvgisprototype.cli.print import print_hour_angle_table_2

from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import DATA_TYPE_DEFAULT, ZERO_NEGATIVE_SOLAR_INCIDENCE_ANGLES_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import QUIET_FLAG_DEFAULT
from pandas import DatetimeIndex
from pvgisprototype.cli.typer.statistics import typer_option_statistics
from pvgisprototype.constants import STATISTICS_FLAG_DEFAULT
from pvgisprototype.constants import CSV_PATH_DEFAULT
from pvgisprototype.constants import INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT
from pvgisprototype.constants import RANDOM_TIMESTAMPS_FLAG_DEFAULT
from pvgisprototype.cli.typer.data_processing import typer_option_dtype
from pvgisprototype.cli.typer.data_processing import typer_option_array_backend
from pvgisprototype.cli.typer.plot import typer_option_uniplot
from pvgisprototype.cli.typer.plot import typer_option_uniplot_terminal_width
from pvgisprototype.constants import UNIPLOT_FLAG_DEFAULT
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.cli.typer.output import typer_option_panels_output
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.verbosity import typer_option_quiet
from pvgisprototype.cli.typer.output import typer_option_index
from pathlib import Path
from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_random_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_periods
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from datetime import datetime
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.cli.typer.output import typer_option_fingerprint
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT
from pvgisprototype.cli.typer.output import typer_option_command_metadata
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call


@log_function_call
def hour_angle(
    longitude: Annotated[float, typer_argument_longitude],
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(now_utc_datetimezone()),
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,  # Used by a callback function
    periods: Annotated[Optional[int], typer_option_periods] = None,  # Used by a callback function
    frequency: Annotated[Optional[str], typer_option_frequency] = None,  # Used by a callback function
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,  # Used by a callback function
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_timestamps: Annotated[bool, typer_option_random_timestamps] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    solar_position_model: Annotated[List[SolarPositionModel], typer_option_solar_position_model] = [SolarPositionModel.noaa],
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.milne,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    group_models: Annotated[Optional[bool], 'Visually cluster time series results per model'] = False,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, 'Resample large time series?'] = False,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = False,
    panels: Annotated[bool, typer_option_panels_output] = False,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
):
    """Calculate the hour angle 'ω = (ST / 3600 - 12) * 15 * π / 180'

    The hour angle (ω) is the angle at any instant through which the earth has
    to turn to bring the meridian of the observer directly in line with the
    sun's rays measured in radian. In other words, it is a measure of time,
    expressed in angular measurement, usually degrees, from solar noon. It
    increases by 15° per hour, negative before solar noon and positive after
    solar noon.
    """
    # Initialize with None ---------------------------------------------------
    user_requested_timestamps = None
    user_requested_timezone = None
    # -------------------------------------------- Smarter way to do this? ---
    
    utc_zoneinfo = ZoneInfo("UTC")
    if timestamps.tz != utc_zoneinfo:

        # Note the input timestamp and timezone
        user_requested_timestamps = timestamps
        user_requested_timezone = timezone

        timestamps = timestamps.tz_localize(utc_zoneinfo)
        timezone = utc_zoneinfo
        logger.info(f'Input timestamps & zone ({user_requested_timestamps} & {user_requested_timezone}) converted to {timestamps} for all internal calculations!')
    solar_position_models = select_models(SolarPositionModel, solar_position_model)  # Using a callback fails!
    solar_hour_angle_series = calculate_solar_hour_angle_series(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_models=solar_position_models,
        solar_time_model=solar_time_model,
        angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    if not quiet:
        from pvgisprototype.cli.print import print_solar_position_series_table
        print_solar_position_series_table(
            longitude=longitude,
            latitude=None,
            timestamps=timestamps,
            timezone=timezone,
            table=solar_hour_angle_series,
            position_parameters=[SolarPositionParameter.hour_angle],
            title='Solar Position Overview',
            index=index,
            surface_orientation=True,
            surface_tilt=True,
            incidence=True,
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
            latitude=None,
            timestamps=timestamps,
            timezone=timezone,
            table=solar_hour_angle_series,
            timing=True,
            declination=True,
            hour_angle=True,
            zenith=True,
            altitude=True,
            azimuth=True,
            surface_orientation=True,
            surface_tilt=True,
            incidence=True,
            user_requested_timestamps=user_requested_timestamps, 
            user_requested_timezone=user_requested_timezone,
            # rounding_places=rounding_places,
            # group_models=group_models,
            filename=csv,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_solar_position_series
        uniplot_solar_position_series(
            solar_position_series=solar_hour_angle_series,
            position_parameters=[SolarPositionParameter.hour_angle],
            timestamps=timestamps,
            surface_orientation=True,
            surface_tilt=True,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle='Solar Hour Angle Series',
            title="Solar Hour Angle",
            label='Hour Angle',
            legend_labels=None,
            terminal_width_fraction=terminal_width_fraction,
            verbose=verbose,
        )
