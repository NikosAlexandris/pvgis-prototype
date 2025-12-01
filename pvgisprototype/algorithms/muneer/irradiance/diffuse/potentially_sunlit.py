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
from pvgisprototype import (
    SurfaceOrientation,
)
from pvgisprototype.log import log_function_call, logger
from pvgisprototype.api.position.models import (
    ShadingState,
)
from math import sin
import numpy as np


@log_function_call
def calculate_diffuse_inclined_irradiance_potentially_sunlit(
    surface_orientation,
    surface_tilt,
    solar_azimuth,
    solar_altitude,
    shading_states,
    shading_state_series,
    diffuse_inclined_irradiance,
    diffuse_sky_irradiance,
    kb_series,
    diffuse_horizontal_irradiance,
):
    """
    """
    if ShadingState.potentially_sunlit in shading_states:
        mask_potentially_sunlit_surface_series = np.logical_and(
                solar_altitude.radians > 0,  #  sun above horizon
            solar_altitude.radians < 0.1,  #  radians or < 5.7 degrees
            shading_state_series == None  # operate only on unset elements
        )
        # else:  # if solar altitude < 0.1 : potentially sunlit surface series
        if np.any(mask_potentially_sunlit_surface_series):
            shading_state_series[mask_potentially_sunlit_surface_series] = ShadingState.potentially_sunlit.value
            logger.info(
                f"Shading state series including {ShadingState.potentially_sunlit.value} :\n{shading_state_series}",
                alt=f"[bold]Shading state[/bold] series including [bold orange]{ShadingState.potentially_sunlit.value}[/bold orange] :\n{shading_state_series}",
            )
            # requires the solar azimuth
            # Normalize the azimuth difference to be within the range -pi to pi
            # A0 : solar azimuth _measured from East_ in radians
            # ALN : angle between the vertical surface containing the normal to the
            #   surface and vertical surface passing through the centre of the solar
            #   disc [rad]
            if isinstance(surface_orientation, SurfaceOrientation):
                surface_orientation = surface_orientation.value
            
            azimuth_difference_series = (
                    solar_azimuth.value - surface_orientation
                )
            azimuth_difference_series = np.arctan2(
                np.sin(azimuth_difference_series),
                np.cos(azimuth_difference_series),
            )
            diffuse_inclined_irradiance[
                mask_potentially_sunlit_surface_series
            ] = diffuse_horizontal_irradiance.value[
                mask_potentially_sunlit_surface_series
            ] * (
                diffuse_sky_irradiance[mask_potentially_sunlit_surface_series]
                * (1 - kb_series[mask_potentially_sunlit_surface_series])
                + kb_series[mask_potentially_sunlit_surface_series]
                * sin(surface_tilt)
                * np.cos(
                    azimuth_difference_series[
                        mask_potentially_sunlit_surface_series
                    ]
                )
                / (
                    0.1
                    - 0.008
                    * solar_altitude.radians[
                        mask_potentially_sunlit_surface_series
                    ]
                )
            )

    return diffuse_inclined_irradiance

