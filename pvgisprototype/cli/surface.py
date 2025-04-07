from datetime import datetime
from pathlib import Path
from typing import Annotated
from zoneinfo import ZoneInfo

import typer
from pandas import DatetimeIndex, Timestamp
from rich.console import Console
from pvgisprototype import (
    LinkeTurbidityFactor,
    SpectralFactorSeries,
    TemperatureSeries,
    WindSpeedSeries,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.api.irradiance.diffuse.horizontal_from_sarah import read_horizontal_irradiance_components_from_sarah
from pvgisprototype.api.series.time_series import get_time_series
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
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
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.surface.positioning import optimise_surface_position
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.cli.typer.albedo import typer_option_albedo
from pvgisprototype.cli.typer.data_processing import (
    typer_option_array_backend,
    typer_option_dtype,
    typer_option_multi_thread,
)
from pvgisprototype.cli.typer.earth_orbit import (
    typer_option_eccentricity_correction_factor,
    typer_option_perigee_offset,
    typer_option_solar_constant,
)
from pvgisprototype.cli.typer.efficiency import (
    typer_option_efficiency,
    typer_option_module_temperature_algorithm,
    typer_option_pv_power_algorithm,
    typer_option_system_efficiency,
)
from pvgisprototype.cli.typer.group import OrderCommands
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
    typer_option_version,
    typer_option_fingerprint,
    typer_option_index,
    typer_option_quick_response,
    typer_option_rounding_places,
)
from pvgisprototype.cli.typer.photovoltaic import (
    typer_option_photovoltaic_module_model,
    typer_option_photovoltaic_module_peak_power,
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
from pvgisprototype.cli.typer.profiling import typer_option_profiling
from pvgisprototype.cli.typer.refraction import (
    typer_option_apply_atmospheric_refraction,
    typer_option_refracted_solar_zenith,
)
from pvgisprototype.cli.typer.spectral_factor import (
    typer_argument_spectral_factor_series,
)
from pvgisprototype.cli.typer.statistics import (
    typer_option_analysis,
    typer_option_groupby,
    typer_option_nomenclature,
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
    ANALYSIS_FLAG_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    CSV_PATH_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEGREES,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    EFFICIENCY_FACTOR_DEFAULT,
    FINGERPRINT_FLAG_DEFAULT,
    GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    GROUPBY_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    METADATA_FLAG_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    NOMENCLATURE_FLAG_DEFAULT,
    NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    OPTIMISER_PRECISION_GOAL,
    PEAK_POWER_DEFAULT,
    PERIGEE_OFFSET,
    PHOTOVOLTAIC_MODULE_DEFAULT,
    QUICK_RESPONSE_CODE_FLAG_DEFAULT,
    QUIET_FLAG_DEFAULT,
    RADIANS,
    RANDOM_TIMESTAMPS_FLAG_DEFAULT,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    ROUNDING_PLACES_DEFAULT,
    SOLAR_CONSTANT,
    SPECTRAL_FACTOR_DEFAULT,
    STATISTICS_FLAG_DEFAULT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SYSTEM_EFFICIENCY_DEFAULT,
    TEMPERATURE_DEFAULT,
    TERMINAL_WIDTH_FRACTION,
    TOLERANCE_DEFAULT,
    UNIPLOT_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    VERSION_FLAG_DEFAULT,
    WIND_SPEED_DEFAULT,
    WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    cPROFILE_FLAG_DEFAULT,
)

app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help="󰶛  Calculate solar surface geometry parameters for a location and moment in time",
)
console = Console()


@app.command(
    "surface-orientation",
    no_args_is_help=True,
    help=":compass: Calculate the solar surface orientation (azimuth) [red]Not implemented![/red]",
)
def surface_orientation():
    """Calculate the surface azimuth angle

    The surface azimuth or orientation (also known as Psi) is the angle between
    the projection on a horizontal plane of the normal to a surface and the
    local meridian, with north through east directions being positive.
    """

    #
    # Update Me
    #

    print("Not implemented")


@app.command(
    "surface-tilt",
    no_args_is_help=True,
    help="Calculate the solar surface tile (slope) [red]Not implemented![/red]",
)
def surface_tilt():
    """Calculate the surface tilt angle

    The surface tilt (or slope, also known as beta) is the angle between the
    plane of the surface and the horizontal plane. A horizontal surface has a
    slope of 0°, and a vertical surface has a slope of 90°.
    """

    #
    # Update Me
    #

    print("Not implemented")


@app.command(
    name="optimise",
    no_args_is_help=True,
)
def optimal_surface_position(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    surface_orientation: Annotated[
        float | None, typer_argument_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
    min_surface_orientation: float = SurfaceOrientation().min_radians,
    max_surface_orientation: float = SurfaceOrientation().max_radians,
    surface_tilt: Annotated[
        float | None, typer_argument_surface_tilt
    ] = SURFACE_TILT_DEFAULT,
    min_surface_tilt: float = SurfaceTilt().min_radians,
    max_surface_tilt: float = SurfaceTilt().max_radians,
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
    global_horizontal_irradiance: Annotated[
        Path | None, typer_option_global_horizontal_irradiance
    ] = None,
    direct_horizontal_irradiance: Annotated[
        Path | None, typer_option_direct_horizontal_irradiance
    ] = None,
    spectral_factor_series: Annotated[
        SpectralFactorSeries, typer_argument_spectral_factor_series
    ] = SPECTRAL_FACTOR_DEFAULT,  # Accept also list of float values ?
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
    linke_turbidity_factor_series: Annotated[
        LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: Annotated[
        bool, typer_option_apply_atmospheric_refraction
    ] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[
        float | None, typer_option_refracted_solar_zenith
    ] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Annotated[float | None, typer_option_albedo] = ALBEDO_DEFAULT,
    apply_reflectivity_factor: Annotated[
        bool, typer_option_apply_reflectivity_factor
    ] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: Annotated[
        SolarPositionModel, typer_option_solar_position_model
    ] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[
        SolarIncidenceModel, typer_option_solar_incidence_model
    ] = SolarIncidenceModel.iqbal,
    zero_negative_solar_incidence_angle: Annotated[
        bool, typer_option_zero_negative_solar_incidence_angle
    ] = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: Annotated[
        SolarTimeModel, typer_option_solar_time_model
    ] = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[
        float, typer_option_eccentricity_correction_factor
    ] = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: Annotated[str, typer_option_angle_output_units] = RADIANS,
    # horizon_heights: Annotated[List[float], typer.Argument(help="Array of horizon elevations.")] = None,
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, typer_option_photovoltaic_module_model
    ] = PHOTOVOLTAIC_MODULE_DEFAULT,  # PhotovoltaicModuleModel.CSI_FREE_STANDING,
    peak_power: Annotated[float, typer_option_photovoltaic_module_peak_power] = PEAK_POWER_DEFAULT,
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
        int, typer_option_rounding_places
    ] = ROUNDING_PLACES_DEFAULT,
    statistics: Annotated[bool, typer_option_statistics] = STATISTICS_FLAG_DEFAULT,
    groupby: Annotated[str | None, typer_option_groupby] = GROUPBY_DEFAULT,
    analysis: Annotated[bool, typer_option_analysis] = ANALYSIS_FLAG_DEFAULT,
    nomenclature: Annotated[
        bool, typer_option_nomenclature
    ] = NOMENCLATURE_FLAG_DEFAULT,
    csv: Annotated[Path, typer_option_csv] = CSV_PATH_DEFAULT,
    uniplot: Annotated[bool, typer_option_uniplot] = UNIPLOT_FLAG_DEFAULT,
    terminal_width_fraction: Annotated[
        float, typer_option_uniplot_terminal_width
    ] = TERMINAL_WIDTH_FRACTION,
    resample_large_series: Annotated[bool, "Resample large time series?"] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT,
    quiet: Annotated[bool, typer_option_quiet] = QUIET_FLAG_DEFAULT,
    log: Annotated[int, typer_option_log] = LOG_LEVEL_DEFAULT,
    version: Annotated[bool, typer_option_version] = VERSION_FLAG_DEFAULT,
    fingerprint: Annotated[bool, typer_option_fingerprint] = FINGERPRINT_FLAG_DEFAULT,
    metadata: Annotated[bool, typer_option_command_metadata] = METADATA_FLAG_DEFAULT,
    quick_response_code: Annotated[
        bool, typer_option_quick_response
    ] = QUICK_RESPONSE_CODE_FLAG_DEFAULT,
    profile: Annotated[bool, typer_option_profiling] = cPROFILE_FLAG_DEFAULT,
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
    method: SurfacePositionOptimizerMethod = SurfacePositionOptimizerMethod.cg,
    number_of_sampling_points: Annotated[int, typer.Option(help="Number of sampleing points")] = NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    iterations: Annotated[int, typer.Option(help="Iterations")] = 100,
    precision_goal: Annotated[float, typer.Option(help="Precision goal")] = OPTIMISER_PRECISION_GOAL,
    sampling_method_shgo: SurfacePositionOptimizerMethodSHGOSamplingMethod = SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
    workers: int = WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
):
    """
    """
    if isinstance(global_horizontal_irradiance, (str, Path)) and isinstance(
        direct_horizontal_irradiance, (str, Path)
    ):  # NOTE This is in the case everything is pathlike
        horizontal_irradiance_components = (
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
        global_horizontal_irradiance = horizontal_irradiance_components[
            GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
        ]
        direct_horizontal_irradiance = horizontal_irradiance_components[
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
        ]
    temperature_series, wind_speed_series, spectral_factor_series = get_time_series(
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        spectral_factor_series=spectral_factor_series,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        mask_and_scale=mask_and_scale,
        in_memory=in_memory,
        dtype=dtype,
        array_backend=array_backend,
        multi_thread=multi_thread,
        verbose=verbose,
        log=log,
    )
    optimal_surface_position = optimise_surface_position(
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
        global_horizontal_irradiance=global_horizontal_irradiance,
        direct_horizontal_irradiance=direct_horizontal_irradiance,
        spectral_factor_series=spectral_factor_series,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        photovoltaic_module=photovoltaic_module,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        mode=mode,
        method=method,
        number_of_sampling_points=number_of_sampling_points,
        iterations=iterations,
        precision_goal=precision_goal,
        sampling_method_shgo=sampling_method_shgo,
        workers=workers,
        angle_output_units=angle_output_units,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )

    if not quiet:
        from pvgisprototype.cli.print.surface import print_surface_position_table

        print_surface_position_table(
            surface_position=optimal_surface_position,
            longitude=longitude,
            latitude=latitude,
            timezone=timezone,
            title="Surface Position",
            version=version,
            fingerprint=fingerprint,
            # surface_orientation=True,
            # surface_tilt=True,
            rounding_places=rounding_places,
        )
