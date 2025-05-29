"""
CLI module to calculate the direct normal irradiance from a horizontal
irradiance component over a location for a period in time.
"""

from datetime import datetime
from pathlib import Path
from typing import Annotated

from pandas import DatetimeIndex, Timestamp
from rich import print

from pvgisprototype.api.irradiance.direct.normal_from_horizontal import (
    calculate_direct_normal_from_horizontal_irradiance_series,
)
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SolarPositionModel,
)
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.cli.typer.data_processing import (
    typer_option_array_backend,
    typer_option_dtype,
)
from pvgisprototype.cli.typer.earth_orbit import (
    typer_option_eccentricity_amplitude,
    typer_option_eccentricity_phase_offset,
)
from pvgisprototype.cli.typer.irradiance import (
    typer_argument_direct_horizontal_irradiance,
)
from pvgisprototype.cli.typer.location import (
    typer_argument_latitude_in_degrees,
    typer_argument_longitude_in_degrees,
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
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
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
)
from pvgisprototype.cli.typer.verbosity import typer_option_quiet, typer_option_verbose
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    CSV_PATH_DEFAULT,
    DATA_TYPE_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    GROUPBY_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    IRRADIANCE_UNIT,
    LOG_LEVEL_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    METADATA_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    PERIGEE_OFFSET,
    QUIET_FLAG_DEFAULT,
    RADIANS,
    RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    STATISTICS_FLAG_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    TOLERANCE_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_function_call


@log_function_call
def get_direct_normal_from_horizontal_irradiance_series(
    direct: Annotated[Path, typer_argument_direct_horizontal_irradiance],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    timestamps: Annotated[DatetimeIndex | None, typer_argument_timestamps] = str(Timestamp.now()),
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
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    neighbor_lookup: Annotated[
        MethodForInexactMatches, typer_option_nearest_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float | None, typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    solar_position_model: Annotated[
        SolarPositionModel, typer_option_solar_position_model
    ] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    eccentricity_phase_offset: Annotated[float, typer_option_eccentricity_phase_offset] = PERIGEE_OFFSET,
    eccentricity_amplitude: Annotated[
        float, typer_option_eccentricity_amplitude
    ] = ECCENTRICITY_CORRECTION_FACTOR,
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
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = METADATA_FLAG_DEFAULT,
) -> None:
    # with progress:
    direct_horizontal_irradiance_series = (
        select_time_series(
            time_series=direct,
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            mask_and_scale=mask_and_scale,
            in_memory=in_memory,
            log=log,
        )
        .to_numpy()
        .astype(dtype=dtype)
    )
    direct_normal_irradiance_series = calculate_direct_normal_from_horizontal_irradiance_series(
        direct_horizontal_irradiance=direct_horizontal_irradiance_series,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        # angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )
    if not quiet:
        if verbose > 0:
            from pvgisprototype.cli.print.irradiance.data import print_irradiance_table_2

            print_irradiance_table_2(
                title=(
                    direct_normal_irradiance_series.title
                    + f" normal irradiance series {IRRADIANCE_UNIT}"
                ),
                irradiance_data=direct_normal_irradiance_series.output,
                timestamps=timestamps,
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = direct_normal_irradiance_series.value.flatten().astype(str)
            csv_str = ",".join(flat_list)
            print(csv_str)
    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics

        print_series_statistics(
            data_array=direct_normal_irradiance_series.value,
            timestamps=timestamps,
            groupby=groupby,
            title=f"Direct normal irradiance series {IRRADIANCE_UNIT}",
            rounding_places=rounding_places,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_series

        uniplot_data_array_series(
            data_array=direct_normal_irradiance_series.value,
            list_extra_data_arrays=None,
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle=direct_normal_irradiance_series.supertitle,
            title=direct_normal_irradiance_series.title,
            label=direct_normal_irradiance_series.label,
            extra_legend_labels=None,
            unit=IRRADIANCE_UNIT,
            terminal_width_fraction=terminal_width_fraction,
        )
    if fingerprint:
        from pvgisprototype.cli.print.fingerprint import print_finger_hash

        print_finger_hash(dictionary=direct_normal_irradiance_series.output)
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
            dictionary=direct_normal_irradiance_series.output,
            filename=csv,
        )
