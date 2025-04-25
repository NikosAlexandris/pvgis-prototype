from math import sin, cos
from numpy import where
from pvgisprototype.log import log_function_call
from pvgisprototype.algorithms.martin_ruiz.reflectivity import (
    calculate_reflectivity_effect,
    calculate_reflectivity_effect_percentage,
    calculate_reflectivity_factor_for_nondirect_irradiance,
)
from pvgisprototype.core.arrays import create_array
from pvgisprototype import GroundReflectedInclinedIrradiance
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    SURFACE_TILT_DEFAULT,
)


@log_function_call
def apply_reflectivity_factor_for_nondirect_irradiance(
    ground_reflected_inclined_irradiance_series: GroundReflectedInclinedIrradiance,
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
) -> GroundReflectedInclinedIrradiance:
    """ """
    # A single reflectivity coefficient
    ground_reflected_irradiance_reflectivity_coefficient = sin(surface_tilt) + (
        surface_tilt - sin(surface_tilt)
    ) / (1 - cos(surface_tilt))

    # The reflectivity factor
    ground_reflected_inclined_irradiance_reflectivity_factor = calculate_reflectivity_factor_for_nondirect_irradiance(
        indirect_angular_loss_coefficient=ground_reflected_irradiance_reflectivity_coefficient,
    )

    # Generate a time series
    ground_reflected_inclined_irradiance_series.reflectivity_factor = create_array(
        ground_reflected_inclined_irradiance_series.value.shape,
        dtype=dtype,
        init_method=ground_reflected_inclined_irradiance_reflectivity_factor,
        backend=array_backend,
    )

    # Apply the reflectivity time series
    ground_reflected_inclined_irradiance_series.value *= (
        ground_reflected_inclined_irradiance_series.reflectivity_factor
    )

    # What is the unmodified quantity ?
    ground_reflected_inclined_irradiance_series.value_before_reflectivity = where(
        ground_reflected_inclined_irradiance_series.reflectivity_factor != 0,
        ground_reflected_inclined_irradiance_series.value
        / ground_reflected_inclined_irradiance_series.reflectivity_factor,
        0,
    )

    # The net effect
    ground_reflected_inclined_irradiance_series.reflectivity = calculate_reflectivity_effect(
        irradiance=ground_reflected_inclined_irradiance_series.value_before_reflectivity,
        reflectivity_factor=ground_reflected_inclined_irradiance_series.reflectivity_factor,
    )

    # Percentage of the net effect
    ground_reflected_inclined_irradiance_series.reflectivity_percentage = calculate_reflectivity_effect_percentage(
        irradiance=ground_reflected_inclined_irradiance_series.value_before_reflectivity,
        reflectivity=ground_reflected_inclined_irradiance_series.reflectivity_factor,
    )

    return ground_reflected_inclined_irradiance_series
