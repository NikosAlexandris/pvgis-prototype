#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from datetime import datetime
from pathlib import Path
from typing import Annotated, List
from zoneinfo import ZoneInfo

from pandas import DatetimeIndex

from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.position.event_time import calculate_event_time_series
from pvgisprototype.api.position.models import (
    SolarEvent,
    SolarPositionModel,
    SolarPositionParameter,
    SolarTimeModel,
    select_models,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.api.datetime.conversion import convert_timestamps_to_utc
from pvgisprototype.cli.typer.data_processing import (
    typer_option_array_backend,
    typer_option_dtype,
)
from pvgisprototype.cli.typer.location import (
    typer_argument_latitude,
    typer_argument_longitude,
)
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.output import (
    typer_option_angle_output_units,
    typer_option_command_metadata,
    typer_option_csv,
    typer_option_fingerprint,
    typer_option_index,
    typer_option_panels_output,
    typer_option_rounding_places,
)
from pvgisprototype.cli.typer.plot import (
    typer_option_uniplot,
    typer_option_uniplot_terminal_width,
)
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.solar_event import typer_option_solar_event
from pvgisprototype.cli.typer.statistics import typer_option_statistics
from pvgisprototype.cli.typer.timestamps import (
    typer_argument_timestamps,
    typer_option_end_time,
    typer_option_frequency,
    typer_option_periods,
    typer_option_random_timestamps,
    typer_option_start_time,
    typer_option_timezone,
)
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.verbosity import typer_option_quiet, typer_option_verbose
from pvgisprototype.cli.typer.validate_output import typer_option_validate_output
from pvgisprototype.constants import (
    ANGLE_OUTPUT_UNITS_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    CSV_PATH_DEFAULT,
    DATA_TYPE_DEFAULT,
    FINGERPRINT_FLAG_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    LOG_LEVEL_DEFAULT,
    QUIET_FLAG_DEFAULT,
    RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    STATISTICS_FLAG_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    TIMEZONE_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_function_call
import typer


@log_function_call
def event_time(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(
        now_utc_datetimezone()
    ),
    start_time: Annotated[
        datetime | None, typer_option_start_time
    ] = None,  # Used by a callback function
    periods: Annotated[
        int | None, typer_option_periods
    ] = None,  # Used by a callback function
    frequency: Annotated[
        str | None, typer_option_frequency
    ] = None,  # Used by a callback function
    end_time: Annotated[
        datetime | None, typer_option_end_time
    ] = None,  # Used by a callback function
    timezone: Annotated[ZoneInfo | None, typer_option_timezone] = TIMEZONE_DEFAULT,
    event: Annotated[List[SolarEvent], typer_option_solar_event] = [None],
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    solar_position_model: Annotated[
        List[SolarPositionModel], typer_option_solar_position_model
    ] = [SolarPositionModel.noaa],
    solar_time_model: Annotated[
        SolarTimeModel, typer_option_solar_time_model
    ] = SolarTimeModel.milne,
    angle_output_units: Annotated[
        str, typer_option_angle_output_units
    ] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[
        int, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    group_models: Annotated[
        bool, "Visually cluster time series results per model"
    ] = False,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, "Resample large time series?"] = False,
    terminal_width_fraction: Annotated[
        float, typer_option_uniplot_terminal_width
    ] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = False,
    panels: Annotated[bool, typer_option_panels_output] = False,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    validate_output: Annotated[bool, typer_option_validate_output] = VALIDATE_OUTPUT_DEFAULT,
):
    """
    """
    utc_timestamps = convert_timestamps_to_utc(
        user_requested_timezone=timezone,
        user_requested_timestamps=timestamps,
    )
    solar_event_time_series = calculate_event_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=utc_timestamps,
        timezone=utc_timestamps.tz,
        event=event,
        dtype=dtype,
        array_backend=array_backend,
        # validate_output=validate_output,
        verbose=verbose,
        log=log,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    if not quiet:
        from pvgisprototype.cli.print.position import print_solar_position_series_table

        print_solar_position_series_table(
            longitude=longitude,
            latitude=None,
            timestamps=utc_timestamps,
            timezone=utc_timestamps.tz,
            table=solar_event_time_series,
            position_parameters=[SolarPositionParameter.event_type, SolarPositionParameter.event_time],
            title="Solar Event Time",
            index=index,
            surface_orientation=True,
            surface_tilt=True,
            incidence=True,
            user_requested_timestamps=timestamps,
            user_requested_timezone=timezone,
            rounding_places=rounding_places,
            group_models=group_models,
            panels=panels,
        )
    if csv:
        from pvgisprototype.cli.write import write_solar_position_series_csv

        write_solar_position_series_csv(
            longitude=longitude,
            latitude=None,
            timestamps=utc_timestamps,
            timezone=utc_timestamps.tz,
            table=solar_event_time_series,
            timing=True,
            declination=True,
            hour_angle=True,
            zenith=True,
            altitude=True,
            azimuth=True,
            surface_orientation=True,
            surface_tilt=True,
            incidence=True,
            user_requested_timestamps=timestamps,
            user_requested_timezone=timezone,
            # rounding_places=rounding_places,
            # group_models=group_models,
            filename=csv,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_solar_position_series

        uniplot_solar_position_series(
            solar_position_series=solar_hour_angle_series,
            position_parameters=[SolarPositionParameter.hour_angle],
            timestamps=utc_timestamps,
            timezone=utc_timestamps.tz,
            surface_orientation=True,
            surface_tilt=True,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle="Solar Hour Angle Series",
            title="Solar Hour Angle",
            label="Hour Angle",
            legend_labels=None,
            terminal_width_fraction=terminal_width_fraction,
            verbose=verbose,
        )

