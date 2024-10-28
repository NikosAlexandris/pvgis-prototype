"""
CLI module to calculate and overview the solar position parameters over a
location for a period in time.
"""

from datetime import datetime
from pathlib import Path
from typing import Annotated, List
from zoneinfo import ZoneInfo

import typer
from pandas import DatetimeIndex

from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.position.models import (
    SolarPositionModel,
    SolarPositionParameter,
    SolarTimeModel,
    select_models,
)
from pvgisprototype.api.position.overview import (
    calculate_solar_position_overview_series,
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
    typer_option_eccentricity_correction_factor,
    typer_option_perigee_offset,
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
    typer_option_solar_position_model,
    typer_option_solar_position_parameter,
    typer_option_sun_to_surface_plane_incidence_angle,
    typer_option_zero_negative_solar_incidence_angle,
)
from pvgisprototype.cli.typer.refraction import (
    typer_option_apply_atmospheric_refraction,
    typer_option_refracted_solar_zenith,
)
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
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    CSV_PATH_DEFAULT,
    DATA_TYPE_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    LOG_LEVEL_DEFAULT,
    PERIGEE_OFFSET,
    QUIET_FLAG_DEFAULT,
    RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    STATISTICS_FLAG_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    TIMEZONE_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger


@log_function_call
def overview(
    ctx: typer.Context,
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
    timezone: Annotated[ZoneInfo | None, typer_option_timezone] = TIMEZONE_DEFAULT,
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
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    solar_position_model: Annotated[
        List[SolarPositionModel], typer_option_solar_position_model
    ] = [SolarPositionModel.noaa],
    position_parameter: Annotated[
        List[SolarPositionParameter], typer_option_solar_position_parameter
    ] = [SolarPositionParameter.all],
    apply_atmospheric_refraction: Annotated[
        bool, typer_option_apply_atmospheric_refraction
    ] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[
        float | None, typer_option_refracted_solar_zenith
    ] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_time_model: Annotated[
        SolarTimeModel, typer_option_solar_time_model
    ] = SolarTimeModel.milne,
    # solar_incidence_model: Annotated[SolarIncidenceModel, typer_option_solar_incidence_model] = SolarIncidenceModel.iqbal,
    complementary_incidence_angle: Annotated[
        bool, typer_option_sun_to_surface_plane_incidence_angle
    ] = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    zero_negative_solar_incidence_angle: Annotated[
        bool, typer_option_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[
        float, typer_option_eccentricity_correction_factor
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
) -> None:
    """ """
    utc_timestamps = convert_timestamps_to_utc(
        user_requested_timezone=timezone,
        user_requested_timestamps=timestamps,
    )
    # Why does the callback function `_parse_model` not work?
    solar_position_models = select_models(
        SolarPositionModel, solar_position_model
    )  # Using a callback fails!
    solar_position_series = calculate_solar_position_overview_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=utc_timestamps,
        timezone=utc_timestamps.tz,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        solar_position_models=solar_position_models,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        # refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        # solar_incidence_model=solar_incidence_model,
        complementary_incidence_angle=complementary_incidence_angle,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        # time_output_units=time_output_units,
        # angle_units=angle_units,
        angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        validate_output=validate_output,
    )
    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    position_parameter = ctx.params.get(
        "position_parameter"
    )  # Bug in Typer that is not passing correctly whatever is in the context ?
    solar_position_parameters = select_models(
        SolarPositionParameter, position_parameter
    )  # Using a callback fails!
    if not quiet:
        from pvgisprototype.cli.print.position import print_solar_position_series_table

        print_solar_position_series_table(
            longitude=longitude,
            latitude=latitude,
            timestamps=utc_timestamps,
            timezone=utc_timestamps.tz,
            table=solar_position_series,
            position_parameters=solar_position_parameters,
            title="Solar Position Overview",
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
            latitude=latitude,
            timestamps=utc_timestamps,
            timezone=utc_timestamps.tz,
            table=solar_position_series,
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
            solar_position_series=solar_position_series,
            position_parameters=solar_position_parameters,
            timestamps=utc_timestamps,
            timezone=utc_timestamps.tz,
            longitude=longitude,
            latitude=latitude,
            surface_orientation=True,
            surface_tilt=True,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle="Solar Position Series",
            title="Solar Position",
            label="Incidence",  # Review Me !
            legend_labels=None,
            terminal_width_fraction=terminal_width_fraction,
            verbose=verbose,
        )
