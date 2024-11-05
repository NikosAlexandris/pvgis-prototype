from pvgisprototype.constants import (
    BEHIND_HORIZON_NAME,
    HORIZON_HEIGHT_NAME,
    NOT_AVAILABLE,
    SHADING_ALGORITHM_NAME,
    VISIBLE_NAME,
)
from pvgisprototype import LocationShading
from pvgisprototype.log import log_function_call


@log_function_call
def generate_dictionary_of_surface_in_shade_series(
        surface_in_shade_series: LocationShading,
        angle_output_units: str,
    ):
    """ """
    return {
        HORIZON_HEIGHT_NAME: (
            getattr(
                surface_in_shade_series.horizon_height, angle_output_units, NOT_AVAILABLE
            )
            if surface_in_shade_series.horizon_height
            else NOT_AVAILABLE
        ),
        BEHIND_HORIZON_NAME: (
            surface_in_shade_series.value if surface_in_shade_series else NOT_AVAILABLE
        ),
        VISIBLE_NAME: (
            ~surface_in_shade_series.value if surface_in_shade_series else NOT_AVAILABLE
        ),
        SHADING_ALGORITHM_NAME: surface_in_shade_series.shading_algorithm,
    }
