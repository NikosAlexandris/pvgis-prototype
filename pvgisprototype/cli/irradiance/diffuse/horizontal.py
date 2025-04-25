"""
CLI module to calculate the diffuse horizontal irradiance component over a
location for a period in time based on external solar irradiance time series.
"""

from datetime import datetime
from pathlib import Path
from typing import Annotated
from zoneinfo import ZoneInfo

from pandas import DatetimeIndex, Timestamp
from rich import print

from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.api.irradiance.diffuse.clear_sky.horizontal import (
    calculate_diffuse_horizontal_irradiance,
)
from pvgisprototype.api.irradiance.diffuse.horizontal import (
    calculate_diffuse_horizontal_irradiance_from_external_data,
)
from pvgisprototype.api.position.models import SolarPositionModel, SolarTimeModel
from pvgisprototype.api.series.horizontal_irradiance import (
    read_horizontal_irradiance_components_from_sarah,
)
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
    convert_float_to_radians_if_requested,
)
from pvgisprototype.cli.typer.data_processing import (
    typer_option_array_backend,
    typer_option_dtype,
    typer_option_multi_thread,
)
from pvgisprototype.cli.typer.earth_orbit import (
    typer_option_solar_constant,
    typer_option_eccentricity_amplitude,
    typer_option_eccentricity_phase_offset,
)
from pvgisprototype.cli.typer.irradiance import (
    typer_option_direct_horizontal_irradiance,
    typer_option_global_horizontal_irradiance,
)
from pvgisprototype.cli.typer.linke_turbidity import (
    typer_option_linke_turbidity_factor_series,
)
from pvgisprototype.cli.typer.location import (
    # typer_argument_elevation,
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
from pvgisprototype.cli.typer.refraction import (
    typer_option_adjust_for_atmospheric_refraction,
    typer_option_refracted_solar_zenith,
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
)
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.verbosity import typer_option_quiet, typer_option_verbose
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    CSV_PATH_DEFAULT,
    DATA_TYPE_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
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
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    SOLAR_CONSTANT,
    STATISTICS_FLAG_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    TOLERANCE_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.arrays import create_array
from pvgisprototype.log import log_function_call


@log_function_call
def get_diffuse_horizontal_irradiance_series(
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    # elevation: Annotated[float, typer_argument_elevation],
    #
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
    timezone: Annotated[ZoneInfo | None, typer_option_timezone] = None,
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    #
    global_horizontal_irradiance: Annotated[
        Path | None, typer_option_global_horizontal_irradiance
    ] = None,
    direct_horizontal_irradiance: Annotated[
        Path | None, typer_option_direct_horizontal_irradiance
    ] = None,
    #
    linke_turbidity_factor_series: Annotated[
        LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    adjust_for_atmospheric_refraction: Annotated[
        bool, typer_option_adjust_for_atmospheric_refraction
    ] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[
        float | None, typer_option_refracted_solar_zenith
    ] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_position_model: Annotated[
        SolarPositionModel, typer_option_solar_position_model
    ] = SolarPositionModel.noaa,
    solar_time_model: Annotated[
        SolarTimeModel, typer_option_solar_time_model
    ] = SolarTimeModel.noaa,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    eccentricity_phase_offset: Annotated[float, typer_option_eccentricity_phase_offset] = PERIGEE_OFFSET,
    eccentricity_amplitude: Annotated[
        float, typer_option_eccentricity_amplitude
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    #
    neighbor_lookup: Annotated[
        MethodForInexactMatches, typer_option_nearest_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float | None, typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    #
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    multi_thread: Annotated[
        bool, typer_option_multi_thread
    ] = MULTI_THREAD_FLAG_DEFAULT,
    #
    rounding_places: Annotated[
        int | None, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[str | None, typer_option_groupby] = GROUPBY_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    #
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    resample_large_series: Annotated[bool, "Resample large time series?"] = False,
    terminal_width_fraction: Annotated[
        float, typer_option_uniplot_terminal_width
    ] = TERMINAL_WIDTH_FRACTION,
    #
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = METADATA_FLAG_DEFAULT,
):
    """Calculate the diffuse horizontal irradiance from SARAH time series.

    Parameters
    ----------
    shortwave: Path
        Filename of surface short-wave (solar) radiation downwards time series
        (short name : `ssrd`) from ECMWF which is the solar radiation that
        reaches a horizontal plane at the surface of the Earth. This parameter
        comprises both direct and diffuse solar radiation.

    direct: Path
        Filename of surface .. time series
        (short name : ``) from ECMWF which is the solar radiation that
        reaches a horizontal plane at the surface of the Earth.

    Returns
    -------
    diffuse_horizontal_irradiance: float
        The diffuse radiant flux incident on a horizontal surface per unit area in W/m².
    """
    # In order to avoid unbound errors
    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": "zeros",
        "backend": array_backend,
    }  # Borrow shape from timestamps
    diffuse_horizontal_irradiance_series = create_array(**array_parameters)
    if isinstance(global_horizontal_irradiance, Path) and isinstance(
        direct_horizontal_irradiance, Path
    ):
        global_horizontal_irradiance_series, direct_horizontal_irradiance_series = (
            read_horizontal_irradiance_components_from_sarah(
                shortwave=global_horizontal_irradiance,
                direct=direct_horizontal_irradiance,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                multi_thread=multi_thread,
                verbose=verbose,
                log=log,
            )
        )
        diffuse_horizontal_irradiance_series = calculate_diffuse_horizontal_irradiance_from_external_data(
            global_horizontal_irradiance_series=global_horizontal_irradiance_series,
            direct_horizontal_irradiance_series=direct_horizontal_irradiance_series,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
        )
    else:
        longitude_in_radians = convert_float_to_radians_if_requested(longitude, RADIANS)
        latitude_in_radians = convert_float_to_radians_if_requested(latitude, RADIANS)
        diffuse_horizontal_irradiance_series = (
            calculate_diffuse_horizontal_irradiance(
                longitude=longitude_in_radians,  # since the input is in degrees,
                latitude=latitude_in_radians,    # yet, as we know, PVGIS-internals expect 'radians' !
                timestamps=timestamps,
                timezone=timezone,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                solar_position_model=solar_position_model,
                solar_time_model=solar_time_model,
                solar_constant=solar_constant,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                angle_output_units=angle_output_units,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                fingerprint=fingerprint,
            )
        )

    longitude = convert_float_to_radians_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_radians_if_requested(latitude, angle_output_units)
    if not quiet:
        if verbose > 0:
            from pvgisprototype.cli.print.irradiance.data import (
                print_irradiance_table_2,
            )

            print_irradiance_table_2(
                title=diffuse_horizontal_irradiance_series.title
                + f" in-plane irradiance series {IRRADIANCE_UNIT}",
                irradiance_data=diffuse_horizontal_irradiance_series.presentation,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = diffuse_horizontal_irradiance_series.value.flatten().astype(str)
            csv_str = ",".join(flat_list)
            print(csv_str)
    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics

        print_series_statistics(
            data_array=diffuse_horizontal_irradiance_series.value,
            timestamps=timestamps,
            groupby=groupby,
            title="Diffuse horizontal irradiance",
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_series

        uniplot_data_array_series(
            data_array=diffuse_horizontal_irradiance_series.value,
            list_extra_data_arrays=None,
            timestamps=timestamps,
            resample_large_series=resample_large_series,
            lines=True,
            supertitle=diffuse_horizontal_irradiance_series.supertitle,
            title=diffuse_horizontal_irradiance_series.title,
            label=diffuse_horizontal_irradiance_series.label,
            extra_legend_labels=None,
            unit=IRRADIANCE_UNIT,
            terminal_width_fraction=terminal_width_fraction,
        )
    if fingerprint:
        from pvgisprototype.cli.print.fingerprint import print_finger_hash

        print_finger_hash(dictionary=diffuse_horizontal_irradiance_series.presentation)
    if metadata:
        import click

        from pvgisprototype.cli.print.metadata import print_command_metadata

        print_command_metadata(context=click.get_current_context())
    # Call write_irradiance_csv() last : it modifies the input dictionary !
    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv

        write_irradiance_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=diffuse_horizontal_irradiance_series.presentation,
            filename=csv,
        )
