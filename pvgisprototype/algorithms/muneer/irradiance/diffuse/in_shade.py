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
from pvgisprototype.constants import (
    TERM_N_IN_SHADE,
)
from pvgisprototype.log import log_function_call, logger
from pvgisprototype.algorithms.muneer.irradiance.diffuse.sky_irradiance import (
    calculate_diffuse_sky_irradiance_series_hofierka,
)
from pvgisprototype.api.position.models import (
    ShadingState,
)
import numpy as np
from numpy import full


@log_function_call
def calculate_diffuse_inclined_irradiance_in_shade(
    timestamps,
    surface_tilt,
    diffuse_inclined_irradiance,
    diffuse_sky_irradiance,
    diffuse_horizontal_irradiance,
    solar_incidence,
    surface_in_shade,
    shading_states,
    shading_state_series,
):
    """
    """
    if ShadingState.in_shade in shading_states:
        #  ----------------------------------------------------- Review Me
        mask_surface_in_shade_series = np.logical_or(
            # np.sin(solar_incidence.radians) < 0,  # in shade
            # will never be True ! when negative incidence angles set to 0 !
            solar_incidence.radians < 0,  # in shade
            # ---------------------------------------------- Review Me ---
            # solar_altitude_series.radians >= 0,  # yet there is ambient light
            surface_in_shade.value  # pre-calculated in-shade moments 
        )
        # Is this the _complementary_ incidence angle series ?
        #  Review Me -----------------------------------------------------
        if np.any(mask_surface_in_shade_series):
            shading_state_series[mask_surface_in_shade_series] = ShadingState.in_shade.value
            logger.info(
                f"Shading state series including {ShadingState.in_shade.value} :\n{shading_state_series}",
                alt=f"[bold]Shading state[/bold] series including [bold white]{ShadingState.in_shade.value}[/bold white] :\n{shading_state_series}",
            )
            diffuse_sky_irradiance[mask_surface_in_shade_series] = (
                calculate_diffuse_sky_irradiance_series_hofierka(
                    n_series=full(timestamps.size, TERM_N_IN_SHADE),
                    surface_tilt=surface_tilt,
                )[mask_surface_in_shade_series]
            )
            diffuse_inclined_irradiance[mask_surface_in_shade_series] = (
                diffuse_horizontal_irradiance.value[mask_surface_in_shade_series]
                * diffuse_sky_irradiance[mask_surface_in_shade_series]
            )

    return diffuse_inclined_irradiance

