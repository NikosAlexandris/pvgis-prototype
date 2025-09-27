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
from pvgisprototype.log import log_function_call, logger
from pvgisprototype.api.position.models import (
    ShadingState,
)
import numpy as np


@log_function_call
def calculate_diffuse_inclined_irradiance_sunlit(
    solar_incidence,
    shading_states,
    solar_altitude,
    shading_state_series,
    diffuse_sky_irradiance,
    kb_series,
    diffuse_inclined_irradiance,
    diffuse_horizontal_irradiance,
):
    """
    """
    if ShadingState.sunlit in shading_states:
        mask_sunlit_surface_series = np.logical_and(
            solar_altitude.radians >= 0.1,  # or >= 5.7 degrees
            shading_state_series == None  # operate only on unset elements
        )
        # else:  # sunlit surface and non-overcast sky
        #     # ----------------------------------------------------------------
        #     solar_azimuth_series = None ?
        #     # ----------------------------------------------------------------
        if np.any(mask_sunlit_surface_series):
            shading_state_series[mask_sunlit_surface_series] = ShadingState.sunlit.value
            logger.info(
                f"Shading state series including {ShadingState.sunlit.value} :\n{shading_state_series}",
                alt=f"[bold]Shading state[/bold] series including [bold yellow]{ShadingState.sunlit.value}[/bold yellow] :\n{shading_state_series}",
            )
            diffuse_inclined_irradiance[
                mask_sunlit_surface_series
            ] = diffuse_horizontal_irradiance.value[mask_sunlit_surface_series] * (
                diffuse_sky_irradiance[mask_sunlit_surface_series]
                * (1 - kb_series[mask_sunlit_surface_series])
                + kb_series[mask_sunlit_surface_series]
                * np.sin(
                    solar_incidence.radians[mask_sunlit_surface_series]
                )  # Should be the _complementary_ incidence angle!
                / np.sin(solar_altitude.radians[mask_sunlit_surface_series])
            )

    return diffuse_inclined_irradiance
