from pathlib import Path
from math import radians
from zoneinfo import ZoneInfo
from pandas import DatetimeIndex
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.datetime.now import now_utc_datetimezone
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
    IN_MEMORY_FLAG_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    SPECTRAL_FACTOR_DEFAULT,
    TEMPERATURE_DEFAULT,
    TOLERANCE_DEFAULT,
    WIND_SPEED_DEFAULT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
)

from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.surface.helpers import (
    calculate_mean_negative_power_output,
    create_bounds_for_optimizer,
    create_dictionary_for_location_parameters,
    create_dictionary_for_result_optimizer,
)
from pvgisprototype.api.surface.optimizer import optimizer
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.constants import (
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    SPECTRAL_FACTOR_DEFAULT,
    TEMPERATURE_DEFAULT,
    WIND_SPEED_DEFAULT,
    ANGLE_OUTPUT_UNITS_DEFAULT,
    NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
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
    timestamps: DatetimeIndex = str(now_utc_datetimezone()),
    timezone: ZoneInfo = ZoneInfo('UTC'),
    global_horizontal_irradiance: Path | None = None,
    direct_horizontal_irradiance: Path | None = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT),
    temperature_series: TemperatureSeries = TemperatureSeries(value=TEMPERATURE_DEFAULT),
    wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
    neighbor_lookup: MethodForInexactMatches = MethodForInexactMatches.nearest,
    tolerance: float | None = TOLERANCE_DEFAULT,
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
    method: SurfacePositionOptimizerMethod = SurfacePositionOptimizerMethod.shgo,
    number_of_sampling_points: int = NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    iterations: int = 1,
    precision_goal: float = 1e-4,
    sampling_method_shgo = SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
    workers: int = WORKERS_FOR_SURFACE_POSITION_OPTIMIZATION,
    angle_output_units: str = ANGLE_OUTPUT_UNITS_DEFAULT,
):
    """
    """
    location_parameters = create_dictionary_for_location_parameters(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        mode=mode,
    )
    bounds = create_bounds_for_optimizer(
        min_surface_orientation=min_surface_orientation,
        max_surface_orientation=max_surface_orientation,
        min_surface_tilt=min_surface_tilt,
        max_surface_tilt=max_surface_tilt,
        mode=mode,
        method=method,
    )
    result_optimizer = optimizer(
        location_parameters=location_parameters,
        func=calculate_mean_negative_power_output,
        global_horizontal_irradiance=global_horizontal_irradiance,
        direct_horizontal_irradiance=direct_horizontal_irradiance,
        spectral_factor_series=spectral_factor_series,
        photovoltaic_module=photovoltaic_module,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
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

    dictionary_optimized_angles = create_dictionary_for_result_optimizer(
        result_optimizer=result_optimizer,
        mode=mode,
        method=method,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        location_parameters=location_parameters,
        angle_output_units=angle_output_units,
    )

    return dictionary_optimized_angles
