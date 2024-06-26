from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype import (
    TemperatureSeries,
    WindSpeedSeries,
    SpectralFactorSeries,
    LinkeTurbidityFactor,
    Longitude,
    Latitude,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.constants import (
    SPECTRAL_FACTOR_DEFAULT,
    TEMPERATURE_DEFAULT,
    WIND_SPEED_DEFAULT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
)

from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel

from pandas import DatetimeIndex
from zoneinfo import ZoneInfo
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.api.surface.helpers import (
    create_dictionary_for_location_parameters,
    create_bounds_for_optimizer,
    calculate_mean_negative_power_output,
    create_dictionary_for_result_optimizer,
)
from pvgisprototype.api.surface.optimizer import optimizer
import math


def optimize_angles(
    longitude: Longitude,
    latitude: Latitude,
    elevation: float, #change it to Elevation
    surface_orientation: SurfaceOrientation = SurfaceOrientation(value=math.radians(180), unit = 'radians'), #SurfaceOrientation().default_radians
    surface_tilt: SurfaceTilt = SurfaceTilt(value=math.radians(45), unit = 'radians'), #SurfaceTilt().default_radians
    min_surface_orientation: float = SurfaceOrientation().min_radians,
    max_surface_orientation: float = SurfaceOrientation().max_radians,
    min_surface_tilt: float = SurfaceTilt().min_radians,
    max_surface_tilt: float = SurfaceTilt().max_radians,
    timestamps: DatetimeIndex = str(now_utc_datetimezone()),
    timezone: ZoneInfo = ZoneInfo('UTC'),
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT),
    temperature_series: TemperatureSeries = TemperatureSeries(value=TEMPERATURE_DEFAULT),
    wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
    method: SurfacePositionOptimizerMethod = SurfacePositionOptimizerMethod.shgo, 
    workers : int = 1,
    sampling_method_shgo = 'sobol'
):
    
    location_parameters = create_dictionary_for_location_parameters(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        spectral_factor_series=spectral_factor_series,
        photovoltaic_module=photovoltaic_module,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
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
        method=method,
        mode=mode,
        bounds=bounds,
        workers=workers,
        sampling_method_shgo=sampling_method_shgo,
    )

    dictionary_optimized_angles = create_dictionary_for_result_optimizer(
        result_optimizer=result_optimizer,
        mode=mode,
        method=method,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        location_parameters=location_parameters,
    )

    return dictionary_optimized_angles
