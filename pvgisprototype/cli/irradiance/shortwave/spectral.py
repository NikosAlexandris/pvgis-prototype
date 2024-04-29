from typing import Annotated, Optional
from datetime import datetime
from pathlib import Path
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.algorithms.pvis.power import calculate_spectrally_resolved_global_inclined_irradiance_series
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithm
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.location import typer_argument_elevation
from pvgisprototype.cli.typer.position import typer_argument_surface_orientation
from pvgisprototype.cli.typer.position import typer_argument_surface_tilt
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_random_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.irradiance import typer_option_global_horizontal_irradiance
from pvgisprototype.cli.typer.irradiance import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer.time_series import typer_option_mask_and_scale
from pvgisprototype.cli.typer.time_series import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer.time_series import typer_option_tolerance
from pvgisprototype.cli.typer.time_series import typer_option_in_memory
from pvgisprototype.cli.typer.linke_turbidity import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.typer.refraction import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer.refraction import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer.albedo import typer_option_albedo
from pvgisprototype.cli.typer.irradiance import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.position import typer_option_solar_incidence_model
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.earth_orbit import typer_option_solar_constant
from pvgisprototype.cli.typer.earth_orbit import typer_option_perigee_offset
from pvgisprototype.cli.typer.earth_orbit import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer.output import typer_option_time_output_units
from pvgisprototype.cli.typer.output import typer_option_angle_units
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.statistics import typer_option_statistics
from pvgisprototype.cli.typer.statistics import typer_option_groupby
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.plot import typer_option_uniplot
from pvgisprototype.cli.typer.plot import typer_option_uniplot_terminal_width
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.log import typer_option_log
from pvgisprototype.cli.typer.output import typer_option_index
from pvgisprototype.cli.typer.output import typer_option_fingerprint
from pvgisprototype.cli.typer.verbosity import typer_option_quiet
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import MULTI_THREAD_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import ALBEDO_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import MINUTES
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import SYSTEM_EFFICIENCY_DEFAULT
from pvgisprototype.constants import EFFICIENCY_DEFAULT
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.cli.typer.timestamps import typer_option_periods
from pandas import DatetimeIndex
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.constants import RANDOM_TIMESTAMPS_FLAG_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.cli.typer.efficiency import typer_option_system_efficiency
from pvgisprototype.cli.typer.efficiency import typer_option_pv_power_algorithm
from pvgisprototype.cli.typer.efficiency import typer_option_module_temperature_algorithm
from pvgisprototype.cli.typer.efficiency import typer_option_efficiency
from pvgisprototype.cli.typer.data_processing import typer_option_dtype
from pvgisprototype.cli.typer.data_processing import typer_option_array_backend
from pvgisprototype.cli.typer.data_processing import typer_option_multi_thread
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import STATISTICS_FLAG_DEFAULT
from pvgisprototype.constants import GROUPBY_DEFAULT
from pvgisprototype.constants import CSV_PATH_DEFAULT
from pvgisprototype.constants import UNIPLOT_FLAG_DEFAULT
from pvgisprototype.constants import TERMINAL_WIDTH_FRACTION
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT
from pvgisprototype.constants import QUIET_FLAG_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT
from pvgisprototype.constants import METADATA_FLAG_DEFAULT
from pvgisprototype.cli.typer.output import typer_option_command_metadata


@log_function_call
def get_spectrally_resolved_global_inclined_irradiance_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(now_utc_datetimezone()),
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,  # Used by a callback function
    periods: Annotated[Optional[int], typer_option_periods] = None,  # Used by a callback function
    frequency: Annotated[Optional[str], typer_option_frequency] = None,  # Used by a callback function
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,  # Used by a callback function
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_timestamps: Annotated[bool, typer_option_random_timestamps] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function
    spectrally_resolved_global_horizontal_irradiance_series: Optional[Path] = None,
    spectrally_resolved_direct_horizontal_irradiance_series: Optional[Path] = None,
    neighbor_lookup: Annotated[MethodForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: Annotated[Optional[float], typer_option_albedo] = ALBEDO_DEFAULT,
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_position_model: Annotated[SolarPositionModel, typer_option_solar_position_model] = SolarPositionModel.noaa,
    solar_incidence_model: Annotated[SolarIncidenceModel, typer_option_solar_incidence_model] = SolarIncidenceModel.iqbal,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SolarTimeModel.noaa,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = MINUTES,
    angle_units: Annotated[str, typer_option_angle_units] = RADIANS,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    system_efficiency: Annotated[Optional[float], typer_option_system_efficiency] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[PVModuleEfficiencyAlgorithm, typer_option_pv_power_algorithm] = PVModuleEfficiencyAlgorithm.king,
    temperature_model: Annotated[ModuleTemperatureAlgorithm, typer_option_module_temperature_algorithm] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[Optional[float], typer_option_efficiency] = EFFICIENCY_DEFAULT,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    multi_thread: Annotated[bool, typer_option_multi_thread] = MULTI_THREAD_FLAG_DEFAULT,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[Optional[str], typer_option_groupby] = GROUPBY_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
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
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        albedo=albedo,
        apply_angular_loss_factor=apply_angular_loss_factor,
        solar_position_model=solar_position_model,
        solar_incidence_model=solar_incidence_model,
        solar_time_model=solar_time_model,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
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
            from pvgisprototype.constants import TITLE_KEY_NAME
            from pvgisprototype.cli.print import print_irradiance_table_2
            print_irradiance_table_2(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                dictionary=spectrally_resolved_global_inclined_irradiance_series.components,
                title = (
                    spectrally_resolved_global_inclined_irradiance_series[
                        TITLE_KEY_NAME
                    ]
                    + f" in-plane irradiance series {IRRADIANCE_UNITS}"
                ),
                rounding_places=rounding_places,
                index=index,
                verbose=verbose,
            )
        else:
            flat_list = spectrally_resolved_global_inclined_irradiance_series.value.flatten().astype(str)
            csv_str = ','.join(flat_list)
            print(csv_str)

    if csv:
        from pvgisprototype.cli.write import write_irradiance_csv
        write_irradiance_csv(
            longitude=None,
            latitude=None,
            timestamps=timestamps,
            dictionary=spectrally_resolved_global_inclined_irradiance_series.components,
            filename=csv,
        )
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
        from pvgisprototype.api.plot import uniplot_data_array_time_series
        uniplot_data_array_time_series(
            data_array=spectrally_resolved_global_inclined_irradiance_series.value,
            list_extra_data_arrays=None,
            lines=True,
            supertitle = 'Global Horizontal Irradiance Series',
            title = 'Global Horizontal Irradiance Series',
            label = 'Global Horizontal Irradiance',
            label_2 = None,
            unit = IRRADIANCE_UNITS,
            terminal_width_fraction=terminal_width_fraction,
        )
    if fingerprint:
        from pvgisprototype.cli.print import print_finger_hash
        print_finger_hash(dictionary=spectrally_resolved_global_inclined_irradiance_series.components)
