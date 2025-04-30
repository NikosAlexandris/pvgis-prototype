from datetime import datetime
from pathlib import Path
from typing import Annotated

from pandas import DatetimeIndex

from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.algorithms.hofierka.power import (
    calculate_spectrally_resolved_global_inclined_irradiance_series,
)
from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import (
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
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
from pvgisprototype.cli.typer.efficiency import (
    typer_option_efficiency,
    typer_option_module_temperature_algorithm,
    typer_option_pv_power_algorithm,
    typer_option_system_efficiency,
)
from pvgisprototype.cli.typer.irradiance import typer_option_apply_reflectivity_factor
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
    typer_option_angle_units,
    typer_option_command_metadata,
    typer_option_csv,
    typer_option_fingerprint,
    typer_option_index,
    typer_option_rounding_places,
    typer_option_time_output_units,
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
)
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
    ALBEDO_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    CSV_PATH_DEFAULT,
    DATA_TYPE_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    EFFICIENCY_FACTOR_DEFAULT,
    FINGERPRINT_FLAG_DEFAULT,
    GROUPBY_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    METADATA_FLAG_DEFAULT,
    MINUTES,
    MULTI_THREAD_FLAG_DEFAULT,
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
    SYSTEM_EFFICIENCY_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    TOLERANCE_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_function_call


@log_function_call
def get_spectrally_resolved_global_inclined_irradiance_series(
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
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    spectrally_resolved_global_horizontal_irradiance_series: Path | None = None,
    spectrally_resolved_direct_horizontal_irradiance_series: Path | None = None,
    neighbor_lookup: Annotated[
        MethodForInexactMatches, typer_option_nearest_neighbor_lookup
    ] = None,
    tolerance: Annotated[float | None, typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    linke_turbidity_factor_series: Annotated[
        LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    adjust_for_atmospheric_refraction: Annotated[
        bool, typer_option_adjust_for_atmospheric_refraction
    ] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[
        float | None, typer_option_refracted_solar_zenith
    ] = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
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
    solar_time_model: Annotated[
        SolarTimeModel, typer_option_solar_time_model
    ] = SolarTimeModel.noaa,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    eccentricity_phase_offset: Annotated[float, typer_option_eccentricity_phase_offset] = PERIGEE_OFFSET,
    eccentricity_amplitude: Annotated[
        float, typer_option_eccentricity_amplitude
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = MINUTES,
    angle_units: Annotated[str, typer_option_angle_units] = RADIANS,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    system_efficiency: Annotated[
        float | None, typer_option_system_efficiency
    ] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[
        PhotovoltaicModulePerformanceModel, typer_option_pv_power_algorithm
    ] = PhotovoltaicModulePerformanceModel.king,
    temperature_model: Annotated[
        ModuleTemperatureAlgorithm, typer_option_module_temperature_algorithm
    ] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[
        float | None, typer_option_efficiency
    ] = EFFICIENCY_FACTOR_DEFAULT,
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
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = METADATA_FLAG_DEFAULT,
):
    """
    Calculate the spectrally resolved global irradiance series over a location
    (latitude), surface and atmospheric conditions, and an arbitrary period of
    time based on spectrally resolved direct (beam), diffuse, reflected solar
    irradiation to account for the varying effects of the solar spectrum.
    Considering shadowing effects of the local topography are optionally
    incorporated.
    """
    spectrally_resolved_global_inclined_irradiance_series = calculate_spectrally_resolved_global_inclined_irradiance_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        spectrally_resolved_global_horizontal_irradiance_series=spectrally_resolved_global_horizontal_irradiance_series,
        spectrally_resolved_direct_horizontal_irradiance_series=spectrally_resolved_direct_horizontal_irradiance_series,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        unrefracted_solar_zenith=unrefracted_solar_zenith,
        albedo=albedo,
        apply_reflectivity_factor=apply_reflectivity_factor,
        solar_position_model=solar_position_model,
        solar_incidence_model=solar_incidence_model,
        solar_time_model=solar_time_model,
        solar_constant=solar_constant,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        system_efficiency=system_efficiency,
        power_model=power_model,
        temperature_model=temperature_model,
        efficiency=efficiency,
        verbose=verbose,
        log=log,
    )
    if not quiet:
        if verbose > 0:
            from pvgisprototype.cli.print.irradiance import print_irradiance_table_2
            from pvgisprototype.constants import TITLE_KEY_NAME

            print_irradiance_table_2(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                dictionary=spectrally_resolved_global_inclined_irradiance_series.components,
                title=(
                    spectrally_resolved_global_inclined_irradiance_series[
                        TITLE_KEY_NAME
                    ]
                    + f" in-plane irradiance series {IRRADIANCE_UNIT}"
                ),
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = spectrally_resolved_global_inclined_irradiance_series.value.flatten().astype(
                str
            )
            csv_str = ",".join(flat_list)
            print(csv_str)
    if statistics:
        from pvgisprototype.api.series.statistics import print_series_statistics

        print_series_statistics(
            data_array=spectrally_resolved_global_inclined_irradiance_series.value,
            timestamps=timestamps,
            groupby=groupby,
            title="Spectrally resolved global irradiance",
            rounding_places=rounding_places,
        )
    if uniplot:
        from pvgisprototype.api.plot import uniplot_data_array_series

        uniplot_data_array_series(
            data_array=spectrally_resolved_global_inclined_irradiance_series.value,
            lines=True,
            supertitle=spectrally_resolved_global_inclined_irradiance_series.supertitle,
            title=spectrally_resolved_global_inclined_irradiance_series.title,
            label=spectrally_resolved_global_inclined_irradiance_series.label,
            extra_legend_labels=None,
            unit=IRRADIANCE_UNIT,
            terminal_width_fraction=terminal_width_fraction,
        )
    if fingerprint:
        from pvgisprototype.cli.print.fingerprint import print_finger_hash

        print_finger_hash(
            dictionary=spectrally_resolved_global_inclined_irradiance_series.components
        )
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
            dictionary=spectrally_resolved_global_inclined_irradiance_series.components,
            filename=csv,
        )
