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
"""
CLI module to calculate the solar incidence angle for a solar surface at a
location, orientation, tilt and moment in time.
"""

from datetime import datetime
from math import pi
from pathlib import Path
from typing import Annotated, List
from zoneinfo import ZoneInfo

from pandas import DatetimeIndex
from xarray import DataArray

from pvgisprototype import SurfaceOrientation, SurfaceTilt
from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.position.incidence import calculate_solar_incidence_series
from pvgisprototype.api.position.models import (
    SolarIncidenceModel,
    SolarPositionParameter,
    SolarTimeModel,
    select_models,
    ShadingModel,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.api.datetime.conversion import convert_timestamps_to_utc
from pvgisprototype.cli.typer.data_processing import (
    typer_option_array_backend,
    typer_option_dtype,
)
from pvgisprototype.cli.typer.earth_orbit import (
    typer_option_eccentricity_amplitude,
    typer_option_eccentricity_phase_offset,
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
from pvgisprototype.cli.typer.position import (
    typer_argument_surface_orientation,
    typer_argument_surface_tilt,
    typer_option_random_surface_orientation,
    typer_option_random_surface_tilt,
    typer_option_solar_incidence_model,
    typer_option_sun_to_surface_plane_incidence_angle,
    typer_option_zero_negative_solar_incidence_angle,
)
from pvgisprototype.cli.typer.shading import(
    typer_option_horizon_profile,
    typer_option_shading_model,
)
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
    COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    CSV_PATH_DEFAULT,
    DATA_TYPE_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    LOG_LEVEL_DEFAULT,
    ECCENTRICITY_PHASE_OFFSET,
    QUIET_FLAG_DEFAULT,
    RADIANS,
    RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    TIMEZONE_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_function_call


@log_function_call
def incidence(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    surface_orientation: Annotated[
        float | None, typer_argument_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
    random_surface_orientation: Annotated[
        bool, typer_option_random_surface_orientation
    ] = False,
    surface_tilt: Annotated[
        float | None, typer_argument_surface_tilt
    ] = SURFACE_TILT_DEFAULT,
    random_surface_tilt: Annotated[
        bool, typer_option_random_surface_tilt
    ] = False,
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
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    solar_incidence_model: Annotated[
        List[SolarIncidenceModel], typer_option_solar_incidence_model
    ] = [SolarIncidenceModel.iqbal],
    horizon_profile: Annotated[DataArray | None, typer_option_horizon_profile] = None,
    shading_model: Annotated[
        ShadingModel, typer_option_shading_model] = ShadingModel.pvgis,  # for 'overview' : should be one !
    complementary_incidence_angle: Annotated[
        bool, typer_option_sun_to_surface_plane_incidence_angle
    ] = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: Annotated[
        SolarTimeModel, typer_option_solar_time_model
    ] = SolarTimeModel.milne,
    zero_negative_solar_incidence_angle: Annotated[
        bool, typer_option_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    eccentricity_phase_offset: Annotated[float, typer_option_eccentricity_phase_offset] = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: Annotated[
        float, typer_option_eccentricity_amplitude
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[
        str, typer_option_angle_output_units
    ] = ANGLE_OUTPUT_UNITS_DEFAULT,
    rounding_places: Annotated[
        int | None, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    group_models: Annotated[
        bool, "Visually cluster time series results per model"
    ] = False,
    # statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
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
    """Calculate the angle of solar incidence

    The angle of incidence (also known as theta) is the angle between the
    direct beam of sunlight and the line perpendicular (normal) to the surface.
    If the sun is directly overhead and the surface is flat (horizontal), the
    angle of incidence is 0°.
    """
    utc_timestamps = convert_timestamps_to_utc(
        user_requested_timezone=timezone,
        user_requested_timestamps=timestamps,
    )
    # --------------------------------------------------------------- Idea ---
    # if not given, optimise tilt and orientation... ?
    # ------------------------------------------------------------------------

    if random_surface_orientation:
        import random

        surface_tilt = random.vonmisesvariate(pi, kappa=0)  # radians

    if random_surface_tilt:
        import random

        surface_tilt = random.uniform(0, pi / 2)  # radians

    solar_incidence_models = select_models(
        SolarIncidenceModel, solar_incidence_model
    )  # Using a callback fails!
    solar_incidence_series = calculate_solar_incidence_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=utc_timestamps,
        timezone=utc_timestamps.tz,
        surface_orientation=SurfaceOrientation(
            value=surface_orientation, unit=RADIANS
        ),  # Typer does not easily support custom types !
        surface_tilt=SurfaceTilt(
            value=surface_tilt, unit=RADIANS
        ),  # Typer does not easily support custom types !
        solar_incidence_models=solar_incidence_models,
        horizon_profile=horizon_profile,
        shading_model=shading_model,
        complementary_incidence_angle=complementary_incidence_angle,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        # solar_time_model=solar_time_model,
        eccentricity_amplitude=eccentricity_amplitude,
        eccentricity_phase_offset=eccentricity_phase_offset,
        angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        validate_output=validate_output,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    if not quiet:
        from pvgisprototype.cli.print.position.data import print_solar_position_series_table

        print_solar_position_series_table(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            table=solar_incidence_series,
            position_parameters=[SolarPositionParameter.incidence],
            title="Solar Incidence",
            index=index,
            surface_orientation=None,
            surface_tilt=None,
            incidence=True,
            user_requested_timestamps=timestamps,
            user_requested_timezone=timezone,
            rounding_places=rounding_places,
            group_models=group_models,
            panels=panels,
        )
        # from pvgisprototype.cli.print import print_solar_incidence_series_in_columns
        # print_solar_incidence_series_in_columns(
        #         longitude=longitude,
        #         latitude=latitude,
        #         timestamps=timestamps,
        #         timezone=timezone,
        #         table=solar_incidence_series,
        #         )

    if csv:
        from pvgisprototype.cli.write import write_solar_position_series_csv

        write_solar_position_series_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=utc_timestamps,
            timezone=utc_timestamps.tz,
            table=solar_incidence_series,
            position_parameters=solar_position_parameters,
            # user_requested_timestamps=timestamps,
            # user_requested_timezone=timezone,
            index=index,
            rounding_places=rounding_places,
            # group_models=group_models,
            filename=csv,
        )

    if uniplot:
        from pvgisprototype.api.plot import uniplot_solar_position_series

        uniplot_solar_position_series(
            solar_position_series=solar_incidence_series,
            position_parameters=[SolarPositionParameter.incidence],
            timestamps=timestamps,  # User requested or UTC ?
            surface_orientation=None,
            surface_tilt=None,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle="Solar Position Series",
            title="Solar Position",
            label="Incidence",
            legend_labels=None,
            terminal_width_fraction=terminal_width_fraction,
            verbose=verbose,
        )
