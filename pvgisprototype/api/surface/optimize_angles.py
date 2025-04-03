from pvgisprototype.log import logger
from math import radians
from zoneinfo import ZoneInfo
from numpy import ndarray
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray

from pvgisprototype import (
    Latitude,
    LinkeTurbidityFactor,
    Longitude,
    SpectralFactorSeries,
    SurfaceOrientation,
    SurfaceTilt,
    TemperatureSeries,
    WindSpeedSeries,
)
from pvgisprototype.constants import (
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    SPECTRAL_FACTOR_DEFAULT,
    TEMPERATURE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    WIND_SPEED_DEFAULT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
)

from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.surface.helpers import (
    calculate_negative_mean_power_output,
    build_location_dictionary,
    build_optimiser_output,
)
from pvgisprototype.api.surface.optimizer_bounds import define_optimiser_bounds
from pvgisprototype.api.surface.optimizer import optimizer
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.api.position.models import ShadingModel

from pvgisprototype.constants import (
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    SPECTRAL_FACTOR_DEFAULT,
    TEMPERATURE_DEFAULT,
    WIND_SPEED_DEFAULT,
    ANGLE_OUTPUT_UNITS_DEFAULT,
    NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    NUMBER_OF_ITERATIONS_DEFAULT,
)


def optimize_angles(
    longitude: Longitude,
    latitude: Latitude,
    elevation: float,  # change it to Elevation
    surface_orientation: SurfaceOrientation = SurfaceOrientation(
        value=radians(180), unit="radians"
    ),  # SurfaceOrientation().default_radians
    surface_tilt: SurfaceTilt = SurfaceTilt(
        value=radians(45), unit="radians"
    ),  # SurfaceTilt().default_radians
    min_surface_orientation: float = SurfaceOrientation().min_radians,
    max_surface_orientation: float = SurfaceOrientation().max_radians,
    min_surface_tilt: float = SurfaceTilt().min_radians,
    max_surface_tilt: float = SurfaceTilt().max_radians,
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo = ZoneInfo('UTC'),
    global_horizontal_irradiance: ndarray | None = None,
    direct_horizontal_irradiance: ndarray | None = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT),
    temperature_series: TemperatureSeries = TemperatureSeries(value=TEMPERATURE_DEFAULT),
    wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,    
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
    method: SurfacePositionOptimizerMethod = SurfacePositionOptimizerMethod.shgo,
    number_of_sampling_points: int = NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    iterations: int = NUMBER_OF_ITERATIONS_DEFAULT,
    precision_goal: float = 1e-4,
    sampling_method_shgo = SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
    workers: int = WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
    angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    # log: int = LOG_LEVEL_DEFAULT,
    # fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
):
    """
    """
    location_parameters = build_location_dictionary(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        mode=mode,
    )
    # if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
    #     logger.info(
    #         f"i Define bounds for the \'{method}\' optimiser ..",
    #         alt=f"i [bold]Define[/bold] bounds for the [magenta]{method}[/magenta] optimiser .."
    #     )
    bounds = define_optimiser_bounds(
        min_surface_orientation=min_surface_orientation,
        max_surface_orientation=max_surface_orientation,
        min_surface_tilt=min_surface_tilt,
        max_surface_tilt=max_surface_tilt,
        mode=mode,
        method=method,
    )
    optimal_angles = optimizer(
        location_parameters=location_parameters,
        func=calculate_negative_mean_power_output,
        global_horizontal_irradiance=global_horizontal_irradiance,
        direct_horizontal_irradiance=direct_horizontal_irradiance,
        spectral_factor_series=spectral_factor_series,
        photovoltaic_module=photovoltaic_module,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        horizon_profile=horizon_profile,
        shading_model=shading_model,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        method=method,
        mode=mode,
        bounds=bounds,
        number_of_sampling_points=number_of_sampling_points,
        iterations=iterations,
        precision_goal=precision_goal,
        sampling_method_shgo=sampling_method_shgo,
        workers=workers,
    )
    optimal_position = build_optimiser_output(
        result_optimizer=optimal_angles,
        mode=mode,
        method=method,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        location_parameters=location_parameters,
        angle_output_units=angle_output_units,
    )

    # if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
    #     from devtools import debug
    #     debug(locals())

    return optimal_position
