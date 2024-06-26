from pathlib import Path
from pvgisprototype import (
    TemperatureSeries,
    WindSpeedSeries,
    SpectralFactorSeries,
    LinkeTurbidityFactor,
    SurfaceTilt,
)
from scipy import optimize
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMode,
)
from typing import Callable, Optional

from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT, LINKE_TURBIDITY_TIME_SERIES_DEFAULT, MASK_AND_SCALE_FLAG_DEFAULT, NEIGHBOR_LOOKUP_DEFAULT, SPECTRAL_FACTOR_DEFAULT, TEMPERATURE_DEFAULT, TOLERANCE_DEFAULT, WIND_SPEED_DEFAULT


def optimizer(
    location_parameters: dict,
    func: Callable,
    global_horizontal_irradiance: Optional[Path] = None,
    direct_horizontal_irradiance: Optional[Path] = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT),
    temperature_series: TemperatureSeries = TemperatureSeries(value=TEMPERATURE_DEFAULT),
    wind_speed_series: WindSpeedSeries = WindSpeedSeries(value=WIND_SPEED_DEFAULT),
    neighbor_lookup: MethodForInexactMatches = MethodForInexactMatches.nearest,
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
    photovoltaic_module: PhotovoltaicModuleModel = PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(value = LINKE_TURBIDITY_TIME_SERIES_DEFAULT),
    method: SurfacePositionOptimizerMethod = SurfacePositionOptimizerMethod.shgo,
    iterations: int = 100,
    mode: SurfacePositionOptimizerMode = SurfacePositionOptimizerMode.Tilt,
    bounds: optimize.Bounds = optimize.Bounds(
        lb=SurfaceTilt().min_radians, ub=SurfaceTilt().max_radians
    ),
    workers: int = 1,
    sampling_method_shgo: str = "sobol",
):
    if method == SurfacePositionOptimizerMethod.shgo:
        result = optimize.shgo(
            func=func,
            bounds=bounds,
            n=iterations,
            args=(
                location_parameters,
                global_horizontal_irradiance,
                direct_horizontal_irradiance,
                spectral_factor_series,
                temperature_series,
                wind_speed_series,
                neighbor_lookup,
                tolerance,
                mask_and_scale,
                in_memory,
                linke_turbidity_factor_series,
                photovoltaic_module,
                mode,
                ),
            sampling_method=sampling_method_shgo,
            workers=workers,
            options={"disp": True},
        )

    if method == SurfacePositionOptimizerMethod.brute:
        result = optimize.brute(
            func=func,
            ranges=bounds,
            args=(
                location_parameters,
                global_horizontal_irradiance,
                direct_horizontal_irradiance,
                spectral_factor_series,
                temperature_series,
                wind_speed_series,
                neighbor_lookup,
                tolerance,
                mask_and_scale,
                in_memory,
                linke_turbidity_factor_series,
                photovoltaic_module,
                mode,
                ),
            finish=None,
            workers=workers,
        )
    else:
        # watch out for when the method passed is not shgo or brute. FIX THIS
        pass
    return result
