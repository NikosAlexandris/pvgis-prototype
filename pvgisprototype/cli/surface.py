import typer
from typing import Annotated, Optional, Union, List
from rich.console import Console
from pathlib import Path
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.api.surface.optimize_angles import optimize_angles
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.api.position.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.cli.typer.data_processing import typer_option_dtype
from pvgisprototype.cli.typer.data_processing import typer_option_array_backend
from pvgisprototype.cli.typer.data_processing import typer_option_multi_thread

from pvgisprototype.cli.typer.location import typer_argument_latitude
from pvgisprototype.cli.typer.location import typer_argument_longitude
from pvgisprototype.cli.typer.location import typer_argument_elevation
from pvgisprototype.cli.typer.position import typer_argument_surface_orientation
from pvgisprototype.cli.typer.position import typer_argument_surface_tilt
from pvgisprototype.cli.typer.position import typer_option_surface_tilt_multi
from pvgisprototype.cli.typer.position import typer_option_surface_orientation_multi
# from pvgisprototype.cli.typer.location import typer_argument_horizon_heights
from pvgisprototype.cli.typer.timestamps import typer_argument_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_random_timestamps
from pvgisprototype.cli.typer.timestamps import typer_option_start_time
from pvgisprototype.cli.typer.timestamps import typer_option_periods
from pvgisprototype.cli.typer.timestamps import typer_option_frequency
from pvgisprototype.cli.typer.timestamps import typer_option_end_time
from pvgisprototype.cli.typer.timestamps import typer_option_timezone
from pvgisprototype.cli.typer.irradiance import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer.irradiance import typer_option_global_horizontal_irradiance
from pvgisprototype.cli.typer.irradiance import typer_option_apply_reflectivity_factor
from pvgisprototype.cli.typer.timing import typer_option_solar_time_model
from pvgisprototype.cli.typer.time_series import typer_option_mask_and_scale
from pvgisprototype.cli.typer.time_series import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer.time_series import typer_option_tolerance
from pvgisprototype.cli.typer.time_series import typer_option_in_memory
from pvgisprototype.cli.typer.temperature import typer_argument_temperature_series
from pvgisprototype.cli.typer.wind_speed import typer_argument_wind_speed_series
from pvgisprototype.cli.typer.earth_orbit import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer.earth_orbit import typer_option_solar_constant
from pvgisprototype.cli.typer.earth_orbit import typer_option_perigee_offset
from pvgisprototype.cli.typer.position import typer_option_solar_incidence_model
from pvgisprototype.cli.typer.position import typer_option_zero_negative_solar_incidence_angle
from pvgisprototype.cli.typer.position import typer_option_solar_position_model
from pvgisprototype.cli.typer.refraction import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer.refraction import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer.linke_turbidity import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.typer.albedo import typer_option_albedo
from pvgisprototype.cli.typer.photovoltaic import typer_option_photovoltaic_module_model
from pvgisprototype.cli.typer.photovoltaic import typer_option_photovoltaic_module_peak_power
from pvgisprototype.cli.typer.efficiency import typer_option_pv_power_algorithm
from pvgisprototype.cli.typer.efficiency import typer_option_module_temperature_algorithm
from pvgisprototype.cli.typer.efficiency import typer_option_efficiency
from pvgisprototype.cli.typer.efficiency import typer_option_system_efficiency
from pvgisprototype.cli.typer.spectral_factor import typer_argument_spectral_factor_series
from pvgisprototype.cli.typer.output import typer_option_angle_output_units
from pvgisprototype.cli.typer.statistics import typer_option_statistics
from pvgisprototype.cli.typer.statistics import typer_option_analysis
from pvgisprototype.cli.typer.statistics import typer_option_nomenclature
from pvgisprototype.cli.typer.statistics import typer_option_groupby
from pvgisprototype.cli.typer.output import typer_option_rounding_places
from pvgisprototype.cli.typer.output import typer_option_index
from pvgisprototype.cli.typer.output import typer_option_quick_response
from pvgisprototype.cli.typer.output import typer_option_fingerprint
from pvgisprototype.cli.typer.verbosity import typer_option_quiet
from pvgisprototype.cli.typer.output import typer_option_csv
from pvgisprototype.cli.typer.plot import typer_option_uniplot
from pvgisprototype.cli.typer.plot import typer_option_uniplot_terminal_width
from pvgisprototype.cli.typer.verbosity import typer_option_verbose
from pvgisprototype.cli.typer.profiling import typer_option_profiling
from pvgisprototype import TemperatureSeries
from pvgisprototype import WindSpeedSeries
from pvgisprototype import SpectralFactorSeries
from pandas import DatetimeIndex
from datetime import datetime
from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.constants import ANALYSIS_FLAG_DEFAULT, EFFICIENCY_FACTOR_DEFAULT, NOMENCLATURE_FLAG_DEFAULT, RANDOM_TIMESTAMPS_FLAG_DEFAULT, ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.constants import cPROFILE_FLAG_DEFAULT
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import MULTI_THREAD_FLAG_DEFAULT
from pvgisprototype.constants import ALBEDO_DEFAULT
from pvgisprototype.constants import ANGULAR_LOSS_FACTOR_FLAG_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import PHOTOVOLTAIC_MODULE_DEFAULT
from pvgisprototype.constants import SPECTRAL_FACTOR_DEFAULT
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SYSTEM_EFFICIENCY_DEFAULT
from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype.cli.typer.output import typer_option_command_metadata

from pvgisprototype.constants import NEIGHBOR_LOOKUP_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT

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
from pvgisprototype.constants import QUICK_RESPONSE_CODE_FLAG_DEFAULT
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT
from pvgisprototype.constants import METADATA_FLAG_DEFAULT
from pvgisprototype.api.surface.parameter_models import SurfacePositionOptimizerMethod, SurfacePositionOptimizerMode
from pvgisprototype.cli.typer.log import typer_option_log


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"󰶛  Calculate solar surface geometry parameters for a location and moment in time",
)
console = Console()


@app.command('surface-orientation', no_args_is_help=True, help=':compass: Calculate the solar surface orientation (azimuth) [red]Not implemented![/red]')
def surface_orientation():
    """Calculate the surface azimuth angle

    The surface azimuth or orientation (also known as Psi) is the angle between
    the projection on a horizontal plane of the normal to a surface and the
    local meridian, with north through east directions being positive.
    """

    #
    # Update Me
    #

    print('Not implemented')


@app.command('surface-tilt', no_args_is_help=True, help='Calculate the solar surface tile (slope) [red]Not implemented![/red]')
def surface_tilt():
    """Calculate the surface tilt angle

    The surface tilt (or slope, also known as beta) is the angle between the
    plane of the surface and the horizontal plane. A horizontal surface has a
    slope of 0°, and a vertical surface has a slope of 90°.
    """

    #
    # Update Me
    #

    print('Not implemented')


from pvgisprototype import SurfaceOrientation
from pvgisprototype import SurfaceTilt


@app.command(
     name="optimise",
     no_args_is_help=True,
)
def optmise_surface_position(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    min_surface_orientation: float = SurfaceOrientation().min_radians,
    max_surface_orientation: float = SurfaceOrientation().max_radians,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    min_surface_tilt: float = SurfaceTilt().min_radians,
    max_surface_tilt: float = SurfaceTilt().max_radians,
    timestamps: Annotated[DatetimeIndex, typer_argument_timestamps] = str(now_utc_datetimezone()),
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,  # Used by a callback function
    periods: Annotated[Optional[int], typer_option_periods] = None,  # Used by a callback function
    frequency: Annotated[Optional[str], typer_option_frequency] = None,  # Used by a callback function
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,  # Used by a callback function
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_timestamps: Annotated[bool, typer_option_random_timestamps] = RANDOM_TIMESTAMPS_FLAG_DEFAULT,  # Used by a callback function

    global_horizontal_irradiance: Annotated[Optional[Path], typer_option_global_horizontal_irradiance] = None,
    direct_horizontal_irradiance: Annotated[Optional[Path], typer_option_direct_horizontal_irradiance] = None,
    spectral_factor_series: Annotated[Path|SpectralFactorSeries, typer_argument_spectral_factor_series] = SPECTRAL_FACTOR_DEFAULT,  # Accept also list of float values ?
    temperature_series: Annotated[Path|TemperatureSeries, typer_argument_temperature_series] = TEMPERATURE_DEFAULT,
    wind_speed_series: Annotated[Path|WindSpeedSeries, typer_argument_wind_speed_series] = WIND_SPEED_DEFAULT,
    neighbor_lookup: Annotated[MethodForInexactMatches, typer_option_nearest_neighbor_lookup] = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Annotated[Optional[float], typer_option_albedo] = ALBEDO_DEFAULT,
    apply_reflectivity_factor: Annotated[Optional[bool], typer_option_apply_reflectivity_factor] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: Annotated[SolarPositionModel, typer_option_solar_position_model] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[SolarIncidenceModel, typer_option_solar_incidence_model] = SolarIncidenceModel.iqbal,
    zero_negative_solar_incidence_angle: Annotated[bool, typer_option_zero_negative_solar_incidence_angle] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: Annotated[SolarTimeModel, typer_option_solar_time_model] = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    # horizon_heights: Annotated[List[float], typer.Argument(help="Array of horizon elevations.")] = None,
    photovoltaic_module: Annotated[PhotovoltaicModuleModel, typer_option_photovoltaic_module_model] = PHOTOVOLTAIC_MODULE_DEFAULT, #PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    peak_power: Annotated[float, typer_option_photovoltaic_module_peak_power] = 1,
    system_efficiency: Annotated[Optional[float], typer_option_system_efficiency] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: Annotated[PhotovoltaicModulePerformanceModel, typer_option_pv_power_algorithm] = PhotovoltaicModulePerformanceModel.king,
    temperature_model: Annotated[ModuleTemperatureAlgorithm, typer_option_module_temperature_algorithm] = ModuleTemperatureAlgorithm.faiman,
    efficiency: Annotated[Optional[float], typer_option_efficiency] = EFFICIENCY_FACTOR_DEFAULT,
    dtype: Annotated[str, typer_option_dtype] = DATA_TYPE_DEFAULT,
    array_backend: Annotated[str, typer_option_array_backend] = ARRAY_BACKEND_DEFAULT,
    multi_thread: Annotated[bool, typer_option_multi_thread] = MULTI_THREAD_FLAG_DEFAULT,
    rounding_places: Annotated[int, typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[Optional[str], typer_option_groupby] = GROUPBY_DEFAULT,
    analysis: Annotated[bool, typer_option_analysis] = ANALYSIS_FLAG_DEFAULT,
    nomenclature: Annotated[bool, typer_option_nomenclature] = NOMENCLATURE_FLAG_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    terminal_width_fraction: Annotated[float, typer_option_uniplot_terminal_width] = TERMINAL_WIDTH_FRACTION,
    resample_large_series: Annotated[bool, 'Resample large time series?'] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = METADATA_FLAG_DEFAULT,
    quick_response_code: Annotated[bool, typer_option_quick_response] = QUICK_RESPONSE_CODE_FLAG_DEFAULT,
    profile: Annotated[bool, typer_option_profiling] = cPROFILE_FLAG_DEFAULT,
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
    method: SurfacePositionOptimizerMethod = SurfacePositionOptimizerMethod.shgo, 
    workers : int = 1,
    sampling_method_shgo = 'sobol'
):
    """
    """
    result = optimize_angles(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        surface_orientation=surface_orientation,
        min_surface_orientation=min_surface_orientation,
        max_surface_orientation=max_surface_orientation,
        surface_tilt=surface_tilt,
        min_surface_tilt=min_surface_tilt,
        max_surface_tilt=max_surface_tilt,
        timestamps=timestamps,
        timezone=timezone,
        spectral_factor_series=spectral_factor_series,
        photovoltaic_module=photovoltaic_module,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        method=SurfacePositionOptimizerMethod.shgo,
        mode=mode,
        sampling_method_shgo="sobol",
    )

    print(f'Optimised angles : {result}')
