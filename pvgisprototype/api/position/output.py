#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
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
