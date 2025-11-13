from typing import Annotated
from fastapi import Depends, HTTPException
from pvgisprototype import (
    LinkeTurbidityFactor,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.api.position.models import (
    ShadingModel,
)
from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.api.surface.positioning import optimise_surface_position
from pvgisprototype.constants import (
    FINGERPRINT_FLAG_DEFAULT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    NUMBER_OF_ITERATIONS_DEFAULT,
    NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
)
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_elevation,
    fastapi_query_end_time,
    fastapi_query_iterations,
    fastapi_query_number_of_samping_points,
    fastapi_query_periods,
    fastapi_query_photovoltaic_module_model,
    fastapi_query_sampling_method_shgo,
    fastapi_query_start_time,
    fastapi_query_surface_position_optimisation_method,
    fastapi_query_surface_position_optimisation_mode,
)
from pvgisprototype.web_api.schemas import (
    Frequency,
    Timezone,
)
from pvgisprototype.web_api.dependency.common_datasets import (
    process_timestamps,
    _read_datasets,
    convert_timestamps_to_specified_timezone,
)
from pvgisprototype.web_api.dependency.location import (
    process_longitude,
    process_latitude,
)
from pvgisprototype.web_api.dependency.position import (
    process_surface_orientation,
    process_surface_tilt,
)
from pvgisprototype.web_api.dependency.time import (
    process_frequency,
    process_timezone,
    process_timezone_to_be_converted,
)
from pvgisprototype.web_api.dependency.shading import (
    process_shading_model,
)
from pvgisprototype.web_api.dependency.meteorology import (
    process_linke_turbidity_factor_series,
)
from pvgisprototype.web_api.dependency.fingerprint import (
    process_fingerprint,
    )


async def process_surface_position_optimisation_method(
    surface_position_optimisation_method: Annotated[
        SurfacePositionOptimizerMethod,
        fastapi_query_surface_position_optimisation_method,
    ] = SurfacePositionOptimizerMethod.l_bfgs_b,
):
    NOT_IMPLEMENTED = [
        SurfacePositionOptimizerMethod.powell,
        SurfacePositionOptimizerMethod.nelder_mead,
        SurfacePositionOptimizerMethod.direct,
    ]

    if surface_position_optimisation_method in NOT_IMPLEMENTED:
        raise HTTPException(
            status_code=400,
            detail=f"Option '{surface_position_optimisation_method.name}' is not currently supported!",
        )

    return surface_position_optimisation_method


async def process_optimise_surface_position(
    _read_datasets: Annotated[dict, Depends(_read_datasets)],
    longitude: Annotated[float, Depends(process_longitude)] = 8.628,
    latitude: Annotated[float, Depends(process_latitude)] = 45.812,
    elevation: Annotated[float, fastapi_query_elevation] = 214.0,
    surface_orientation: Annotated[
        float, Depends(process_surface_orientation)
    ] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Annotated[
        float, Depends(process_surface_tilt)
    ] = SURFACE_TILT_DEFAULT,
    start_time: Annotated[str | None, fastapi_query_start_time] = "2013-01-01",
    periods: Annotated[int | None, fastapi_query_periods] = None,
    frequency: Annotated[Frequency, Depends(process_frequency)] = Frequency.Hourly,
    end_time: Annotated[str | None, fastapi_query_end_time] = "2013-12-31",
    timestamps: Annotated[str | None, Depends(process_timestamps)] = None,
    timezone: Annotated[Timezone, Depends(process_timezone)] = Timezone.UTC,  # type: ignore[attr-defined]
    timezone_for_calculations: Annotated[Timezone, Depends(process_timezone_to_be_converted)] = Timezone.UTC,  # type: ignore[attr-defined]
    user_requested_timestamps: Annotated[
        None, Depends(convert_timestamps_to_specified_timezone)
    ] = None,
    shading_model: Annotated[
        ShadingModel, Depends(process_shading_model)
    ] = ShadingModel.pvgis,
    linke_turbidity_factor_series: Annotated[
        float | LinkeTurbidityFactor, Depends(process_linke_turbidity_factor_series)
    ] = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    photovoltaic_module: Annotated[
        PhotovoltaicModuleModel, fastapi_query_photovoltaic_module_model
    ] = PhotovoltaicModuleModel.CSI_FREE_STANDING,
    surface_position_optimisation_mode: Annotated[
        SurfacePositionOptimizerMode, fastapi_query_surface_position_optimisation_mode
    ] = SurfacePositionOptimizerMode.NoneValue,
    surface_position_optimisation_method: Annotated[
        SurfacePositionOptimizerMethod,
        Depends(process_surface_position_optimisation_method),
    ] = SurfacePositionOptimizerMethod.l_bfgs_b,
    sampling_method_shgo: Annotated[
        SurfacePositionOptimizerMethodSHGOSamplingMethod,
        fastapi_query_sampling_method_shgo,
    ] = SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
    number_of_sampling_points: Annotated[
        int, fastapi_query_number_of_samping_points
    ] = NUMBER_OF_SAMPLING_POINTS_SURFACE_POSITION_OPTIMIZATION,
    iterations: Annotated[int, fastapi_query_iterations] = NUMBER_OF_ITERATIONS_DEFAULT,
    fingerprint: Annotated[
        bool, Depends(process_fingerprint)
    ] = FINGERPRINT_FLAG_DEFAULT,
) -> dict:
    """ """
    if surface_position_optimisation_mode == SurfacePositionOptimizerMode.NoneValue:
        return {}
    else:
        optimal_surface_position = optimise_surface_position(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            min_surface_orientation=SurfaceOrientation().min_radians,
            max_surface_orientation=SurfaceOrientation().max_radians,
            min_surface_tilt=SurfaceTilt().min_radians,
            max_surface_tilt=SurfaceTilt().max_radians,
            global_horizontal_irradiance=_read_datasets[
                "global_horizontal_irradiance_series"
            ],
            direct_horizontal_irradiance=_read_datasets[
                "direct_horizontal_irradiance_series"
            ],
            temperature_series=_read_datasets["temperature_series"],
            wind_speed_series=_read_datasets["wind_speed_series"],
            spectral_factor_series=_read_datasets["spectral_factor_series"],
            horizon_profile=_read_datasets["horizon_profile"],
            shading_model=shading_model,
            timestamps=timestamps,
            timezone=timezone_for_calculations,  # type: ignore
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            photovoltaic_module=photovoltaic_module,
            mode=surface_position_optimisation_mode,
            method=surface_position_optimisation_method,
            sampling_method_shgo=sampling_method_shgo,
            number_of_sampling_points=number_of_sampling_points,
            iterations=iterations,
            fingerprint=fingerprint,
        )

        if (optimal_surface_position["Surface Tilt"] is None) or (  # type: ignore
            optimal_surface_position["Surface Orientation"] is None  # type: ignore
        ):
            raise HTTPException(
                status_code=400,
                detail="Using combination of input could not find optimal surface position",
            )

        return optimal_surface_position  # type: ignore
