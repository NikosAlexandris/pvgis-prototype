from pvgisprototype.api.position.models import SolarPositionParameter
from pvgisprototype.constants import (
    BEHIND_HORIZON_NAME,
    HORIZON_HEIGHT_COLUMN_NAME,
    NOT_AVAILABLE,
    SHADING_ALGORITHM_NAME,
    VISIBLE_COLUMN_NAME,
)
from pvgisprototype import LocationShading
from pvgisprototype.log import log_function_call


@log_function_call
def generate_dictionary_of_surface_in_shade_series(
    surface_in_shade_series: LocationShading,
    angle_output_units,
):
    """ """
    return {
        SolarPositionParameter.horizon: (
            getattr(
                surface_in_shade_series.horizon_height,
                angle_output_units,
                NOT_AVAILABLE,
            )
            if surface_in_shade_series
            else NOT_AVAILABLE
        ),
        # BEHIND_HORIZON_NAME: (
        #     surface_in_shade_series.value if surface_in_shade_series else NOT_AVAILABLE
        # ),
        SolarPositionParameter.visible: (
            ~surface_in_shade_series.value if surface_in_shade_series else NOT_AVAILABLE
        ),
        SHADING_ALGORITHM_NAME: surface_in_shade_series.shading_algorithm,
    }


def generate_dictionary_of_surface_in_shade_series_x(
    surface_in_shade_series: LocationShading,
):
    """ """
    return {
        SolarPositionParameter.horizon: (
            surface_in_shade_series.horizon_height
            if surface_in_shade_series
            else NOT_AVAILABLE
        ),
        SolarPositionParameter.visible: (
            ~surface_in_shade_series.value if surface_in_shade_series else NOT_AVAILABLE
        ),
        SHADING_ALGORITHM_NAME: surface_in_shade_series.shading_algorithm,
    }
