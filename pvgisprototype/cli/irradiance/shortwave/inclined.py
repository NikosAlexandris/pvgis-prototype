"""
CLI module to calculate the global (shortwave) inclined irradiance over a
location for a period in time.
"""

from datetime import datetime
from pathlib import Path
from typing import Annotated

from pandas import DatetimeIndex, Timedelta
from rich import print
from xarray import DataArray

from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.series.horizontal_irradiance import read_horizontal_irradiance_components_from_sarah
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.irradiance.shortwave.inclined import (
    calculate_global_inclined_irradiance,
)
from pvgisprototype.api.position.models import (
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
    ShadingModel,
)
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.cli.typer.albedo import typer_option_albedo
from pvgisprototype.cli.typer.data_processing import (
    typer_option_array_backend,
    typer_option_dtype,
    typer_option_multi_thread,
)
from pvgisprototype.cli.typer.earth_orbit import (
    typer_option_eccentricity_amplitude,
    typer_option_eccentricity_phase_offset,
    typer_option_solar_constant,
)
from pvgisprototype.cli.typer.irradiance import (
    typer_option_apply_reflectivity_factor,
    typer_option_direct_horizontal_irradiance,
    typer_option_global_horizontal_irradiance,
)
from pvgisprototype.cli.typer.linke_turbidity import (
    typer_option_linke_turbidity_factor_series,
)
from pvgisprototype.cli.typer.location import (
    typer_argument_elevation,
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
    typer_option_rounding_places,
)
from pvgisprototype.cli.typer.plot import (
    typer_option_uniplot,
    typer_option_uniplot_terminal_width,
)
from pvgisprototype.cli.typer.position import (
    typer_argument_surface_orientation,
    typer_argument_surface_tilt,
    typer_option_solar_incidence_model,
    typer_option_solar_position_model,
    typer_option_zero_negative_solar_incidence_angle,
)
from pvgisprototype.cli.typer.refraction import (
    typer_option_adjust_for_atmospheric_refraction,
    # typer_option_refracted_solar_zenith,
)
from pvgisprototype.cli.typer.shading import(
    typer_option_horizon_profile,
    typer_option_shading_model,
)
from pvgisprototype.cli.typer.statistics import (
    typer_option_groupby,
    typer_option_statistics,
)
from pvgisprototype.cli.typer.time_series import (
    typer_option_in_memory,
    typer_option_mask_and_scale,
    typer_option_nearest_neighbor_lookup,
    typer_option_tolerance,
)
from pvgisprototype.cli.typer.timestamps import (
    typer_argument_timestamps,
    typer_option_end_time,
    typer_option_frequency,
    typer_option_periods,
    typer_option_random_timestamps,
    typer_option_start_time,
    typer_option_timezone,
    typer_option_time_offset_data,
    typer_option_time_offset_variable,
)
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.validate_output import typer_option_validate_output
from pvgisprototype.cli.typer.verbosity import typer_option_quiet, typer_option_verbose
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    CSV_PATH_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEGREES,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    GROUPBY_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    METADATA_FLAG_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    PERIGEE_OFFSET,
    QUIET_FLAG_DEFAULT,
    RADIANS,
    RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    SOLAR_CONSTANT,
    STATISTICS_FLAG_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    TOLERANCE_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger
import numpy


@log_function_call
def get_global_inclined_irradiance_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    surface_orientation: Annotated[
        float | None, typer_argument_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[
        float | None, typer_argument_surface_tilt
    ] = SURFACE_TILT_DEFAULT,
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
    timezone: Annotated[str | None, typer_option_timezone] = None,
    time_offset_data: Annotated[Timedelta | None, typer_option_time_offset_data] = None,
    time_offset_variable: Annotated[str | None, typer_option_time_offset_variable] = None,
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    global_horizontal_irradiance: Annotated[
        Path | None, typer_option_global_horizontal_irradiance
    ] = None,
    direct_horizontal_irradiance: Annotated[
        Path | None, typer_option_direct_horizontal_irradiance
    ] = None,
    neighbor_lookup: Annotated[
        MethodForInexactMatches | None, typer_option_nearest_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float | None, typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: Annotated[
        LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    adjust_for_atmospheric_refraction: Annotated[
        bool, typer_option_adjust_for_atmospheric_refraction
    ] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    # refracted_solar_zenith: Annotated[
    #     float | None, typer_option_refracted_solar_zenith
    # ] = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: Annotated[float | None, typer_option_albedo] = ALBEDO_DEFAULT,
    apply_reflectivity_factor: Annotated[
        bool, typer_option_apply_reflectivity_factor
    ] = True,
    solar_position_model: Annotated[
        SolarPositionModel, typer_option_solar_position_model
    ] = SolarPositionModel.noaa,
    solar_incidence_model: Annotated[
        SolarIncidenceModel, typer_option_solar_incidence_model
    ] = SolarIncidenceModel.iqbal,
    zero_negative_solar_incidence_angle: Annotated[
        bool, typer_option_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    horizon_profile: Annotated[DataArray | None, typer_option_horizon_profile] = None,
    shading_model: Annotated[
        ShadingModel, typer_option_shading_model] = ShadingModel.pvis,  # for power generation : should be one !
    solar_time_model: Annotated[
        SolarTimeModel, typer_option_solar_time_model
    ] = SolarTimeModel.noaa,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    eccentricity_phase_offset: Annotated[float, typer_option_eccentricity_phase_offset] = PERIGEE_OFFSET,
    eccentricity_amplitude: Annotated[
        float, typer_option_eccentricity_amplitude
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    # horizon_heights: Annotated[List[float], typer.Argument(help="Array of horizon elevations.")] = None,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    multi_thread: Annotated[
        bool, typer_option_multi_thread
    ] = MULTI_THREAD_FLAG_DEFAULT,
    rounding_places: Annotated[
        int | None, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[str | None, typer_option_groupby] = GROUPBY_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, "Resample large time series?"] = False,
    terminal_width_fraction: Annotated[
        float, typer_option_uniplot_terminal_width
    ] = TERMINAL_WIDTH_FRACTION,
    validate_output: Annotated[bool, typer_option_validate_output] = VALIDATE_OUTPUT_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = METADATA_FLAG_DEFAULT,
):
    """Calculate the global horizontal irradiance (GHI)

    The global horizontal irradiance represents the total amount of shortwave
    radiation received from above by a surface horizontal to the ground. It
    includes both the direct and the diffuse solar radiation.
    """
    # # ------------------------------------------------------------------------
    # if global_horizontal_irradiance + direct_horizontal_irradiance are Path objects:
    if isinstance(global_horizontal_irradiance, (str, Path)) and isinstance(
        direct_horizontal_irradiance, (str, Path)
    ):  # NOTE This is in the case everything is pathlike
        global_horizontal_irradiance, direct_horizontal_irradiance = (
            read_horizontal_irradiance_components_from_sarah(
                shortwave=global_horizontal_irradiance,
                direct=direct_horizontal_irradiance,
                longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
                latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
                timestamps=timestamps,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                multi_thread=multi_thread,
                # multi_thread=False,
                verbose=verbose,
                log=log,
            )
        )

    global_inclined_irradiance_series = calculate_global_inclined_irradiance(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        timestamps=timestamps,
        timezone=timezone,
        global_horizontal_irradiance=global_horizontal_irradiance,
        direct_horizontal_irradiance=direct_horizontal_irradiance,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        albedo=albedo,
        apply_reflectivity_factor=apply_reflectivity_factor,
        solar_position_model=solar_position_model,
        solar_incidence_model=solar_incidence_model,
        zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        horizon_profile=horizon_profile,
        shading_model=shading_model,
        solar_time_model=solar_time_model,
        solar_constant=solar_constant,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        # angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        validate_output=validate_output,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )


    if not quiet:
        if verbose > 0:
            longitude = convert_float_to_degrees_if_requested(
                longitude, angle_output_units
            )
            latitude = convert_float_to_degrees_if_requested(
                latitude, angle_output_units
            )
            from pvgisprototype.cli.print.irradiance.data import print_irradiance_table_2

            print_irradiance_table_2(
                title=global_inclined_irradiance_series.title
                + f" in-plane irradiance series {IRRADIANCE_UNIT}",
                irradiance_data=global_inclined_irradiance_series.output,
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                timestamps=timestamps,
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = global_inclined_irradiance_series.value.flatten().astype(str)
            csv_str = ",".join(flat_list)
            print(csv_str)
    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics

        print_series_statistics(
            data_array=global_inclined_irradiance_series.value,
            timestamps=timestamps,
            groupby=groupby,
            title="Global irradiance",
            rounding_places=rounding_places,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_series

        uniplot_data_array_series(
            data_array=global_inclined_irradiance_series.value,
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            frequency=frequency,
            lines=True,
            supertitle=global_inclined_irradiance_series.supertitle,
            title=global_inclined_irradiance_series.title,
            label=global_inclined_irradiance_series.label,
            extra_legend_labels=None,
            unit=IRRADIANCE_UNIT,
            terminal_width_fraction=terminal_width_fraction,
        )
    if fingerprint:
        from pvgisprototype.cli.print.fingerprint import print_finger_hash

        print_finger_hash(dictionary=global_inclined_irradiance_series.output)
    if metadata:
        import click

        from pvgisprototype.cli.print.metadata import print_command_metadata

        print_command_metadata(context=click.get_current_context())
    # Call write_irradiance_csv() last : it modifies the input dictionary !
    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv

        write_irradiance_csv(
            longitude=None,
            latitude=None,
            timestamps=timestamps,
            dictionary=global_inclined_irradiance_series.output,
            filename=csv,
        )
