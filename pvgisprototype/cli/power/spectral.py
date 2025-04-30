from datetime import datetime
from pathlib import Path
from typing import Annotated

from pandas import DatetimeIndex

from pvgisprototype import LinkeTurbidityFactor, TemperatureSeries, WindSpeedSeries
from pvgisprototype.algorithms.hofierka.constants import MINIMUM_SPECTRAL_MISMATCH
from pvgisprototype.algorithms.hofierka.power import (
    calculate_spectral_photovoltaic_power_output,
)
from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.cli.typer.albedo import typer_option_albedo
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
    typer_option_solar_incidence_model,
    typer_option_solar_position_model,
    typer_option_surface_orientation,
    typer_option_surface_tilt,
)
from pvgisprototype.cli.typer.refraction import (
    typer_option_adjust_for_atmospheric_refraction,
    typer_option_refracted_solar_zenith,
)
from pvgisprototype.cli.typer.statistics import (
    typer_option_groupby,
    typer_option_statistics,
)
from pvgisprototype.cli.typer.temperature import typer_argument_temperature_series
from pvgisprototype.cli.typer.time_series import (
    typer_option_in_memory,
    typer_option_mask_and_scale,
    typer_option_nearest_neighbor_lookup,
    typer_option_tolerance,
)

# from pvgisprototype.cli.typer.location import typer_argument_horizon_heights
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
from pvgisprototype.cli.typer.wind_speed import typer_argument_wind_speed_series
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    CSV_PATH_DEFAULT,
    ECCENTRICITY_CORRECTION_FACTOR,
    EFFICIENCY_FACTOR_DEFAULT,
    FINGERPRINT_FLAG_DEFAULT,
    GROUPBY_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    LOG_LEVEL_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    MINUTES,
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
    SYSTEM_EFFICIENCY_DEFAULT,
    TEMPERATURE_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    TOLERANCE_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    WIND_SPEED_DEFAULT,
)


def spectral_photovoltaic_power_output_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    surface_orientation: Annotated[
        float | None, typer_option_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[
        float | None, typer_option_surface_tilt
    ] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(
        now_utc_datetimezone()
    ),
    start_time: Annotated[datetime | None, typer_option_start_time] = None,
    periods: Annotated[int | None, typer_option_periods] = None,
    frequency: Annotated[str | None, typer_option_frequency] = None,
    end_time: Annotated[datetime | None, typer_option_end_time] = None,
    timezone: Annotated[str | None, typer_option_timezone] = None,
    random_timestamps: Annotated[
        bool, typer_option_random_timestamps
    ] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    spectrally_resolved_global_horizontal_irradiance_series: Annotated[
        Path | None, typer_option_global_horizontal_irradiance
    ] = None,
    spectrally_resolved_direct_horizontal_irradiance_series: Annotated[
        Path | None, typer_option_direct_horizontal_irradiance
    ] = None,
    number_of_junctions: int = 1,
    spectral_response_data: Path | None = None,
    standard_conditions_response: Path | None = None,  #: float = 1,  # STCresponse : read from external data
    # extraterrestrial_normal_irradiance_series,  # spectral_ext,
    minimum_spectral_mismatch=MINIMUM_SPECTRAL_MISMATCH,
    temperature_series: Annotated[
        TemperatureSeries, typer_argument_temperature_series
    ] = TEMPERATURE_DEFAULT,
    wind_speed_series: Annotated[
        WindSpeedSeries, typer_argument_wind_speed_series
    ] = WIND_SPEED_DEFAULT,
    neighbor_lookup: Annotated[
        MethodForInexactMatches, typer_option_nearest_neighbor_lookup
    ] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[float | None, typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    # dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    # array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    # multi_thread: Annotated[bool, typer_option_multi_thread] = MULTI_THREAD_FLAG_DEFAULT,
    linke_turbidity_factor_series: Annotated[
        LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series
    ] = None,  # Changed this to np.ndarray
    adjust_for_atmospheric_refraction: Annotated[
        bool, typer_option_adjust_for_atmospheric_refraction
    ] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[
        float | None, typer_option_refracted_solar_zenith
    ] = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Annotated[float | None, typer_option_albedo] = ALBEDO_DEFAULT,
    apply_reflectivity_factor: Annotated[
        bool, typer_option_apply_reflectivity_factor
    ] = True,
    solar_position_model: Annotated[
        SolarPositionModel, typer_option_solar_position_model
    ] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[
        SolarIncidenceModel, typer_option_solar_incidence_model
    ] = SolarIncidenceModel.iqbal,
    solar_time_model: Annotated[
        SolarTimeModel, typer_option_solar_time_model
    ] = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    eccentricity_phase_offset: Annotated[float, typer_option_eccentricity_phase_offset] = PERIGEE_OFFSET,
    eccentricity_amplitude: Annotated[
        float, typer_option_eccentricity_amplitude
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = MINUTES,
    angle_units: Annotated[str, typer_option_angle_units] = RADIANS,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    # horizon_heights: Annotated[List[float], typer.Argument(help="Array of horizon elevations.")] = None,
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
    rounding_places: Annotated[
        int | None, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[str | None, typer_option_groupby] = GROUPBY_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    terminal_width_fraction: Annotated[
        float, typer_option_uniplot_terminal_width
    ] = TERMINAL_WIDTH_FRACTION,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = False,
):
    """
    This method accounts for the effects of the solar spectrum's varying
    wavelengths on PV output, offering a more detailed analysis for systems
    sensitive to specific spectral ranges.
    """
    (
        spectrally_resolved_photovoltaic_power,
        results,
        title,
    ) = calculate_spectral_photovoltaic_power_output(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        spectrally_resolved_global_horizontal_irradiance_series=spectrally_resolved_global_horizontal_irradiance_series,
        spectrally_resolved_direct_horizontal_irradiance_series=spectrally_resolved_direct_horizontal_irradiance_series,
        spectral_response_data=spectral_response_data,
        number_of_junctions=number_of_junctions,
        standard_conditions_response=standard_conditions_response,
        minimum_spectral_mismatch=minimum_spectral_mismatch,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
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
    )
    # longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    # latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)
    if not quiet:
        if verbose > 0:
            pass
        #     print_irradiance_table_2(
        #         longitude=longitude,
        #         latitude=latitude,
        #         timestamps=timestamps,
        #         dictionary=results,
        #         title=title + f' irradiance series {IRRADIANCE_UNIT}',
        #         rounding_places=rounding_places,
        #         index=index,
        #         verbose=verbose,
        #     )
        else:
            flat_list = spectrally_resolved_photovoltaic_power.flatten().astype(str)
            csv_str = ",".join(flat_list)
            print(csv_str)
    # if statistics:
    #     print_series_statistics(
    #         data_array=spectrally_resolved_photovoltaic_power,
    #         timestamps=timestamps,
    #         groupby=groupby,
    #         title="Spectrally resolved photovoltaic power",
    #     )
    # if uniplot:
    #     from pvgisprototype.api.plot import uniplot_data_array_series
    #     uniplot_data_array_series(
    #         data_array=photovoltaic_power_output_series.value,
    #         list_extra_data_arrays=None,
    #         lines=True,
    #         supertitle = 'Photovoltaic Power Output Series',
    #         title="Photovoltaic power output",
    #         label = 'Photovoltaic Power',
    #         label_2 = None,
    #         unit = POWER_UNIT,
    #     )
    # if fingerprint:
    #     from pvgisprototype.cli.print.fingerprint import print_finger_hash
    #     print_finger_hash(dictionary=photovoltaic_power_output_series.components)
    # if metadata:
        # from pvgisprototype.cli.print.metadata import print_command_metadata
    #     import click
    #     print_command_metadata(context = click.get_current_context())
    # Call write_irradiance_csv() last : it modifies the input dictionary !
    # if csv:
    #     write_irradiance_csv(
    #         longitude=longitude,
    #         latitude=latitude,
    #         timestamps=timestamps,
    #         dictionary=results,
    #         filename=csv,
    #     )
