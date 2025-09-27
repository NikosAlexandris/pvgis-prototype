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
import numpy as np
def calculate_azimuth(local_hour_angle, delta, latitude):
    """Calculate the Azimuth (A)

    Examples
    --------
    azimuth_array = calculate_azimuth(local_hour_angle_array, delta_array, latitude_array)
    """
    local_hour_angle_rad = np.radians(local_hour_angle)
    delta_rad = np.radians(delta)
    latitude_rad = np.radians(latitude)
    tan_azimuth = -np.sin(local_hour_angle_rad) / (
        np.tan(delta_rad) * np.cos(latitude_rad)
        - np.sin(latitude_rad) * np.cos(local_hour_angle_rad)
    )
    azimuth = np.degrees(
        np.arctan2(
            -np.sin(local_hour_angle_rad),
            np.tan(delta_rad) * np.cos(latitude_rad)
            - np.sin(latitude_rad) * np.cos(local_hour_angle_rad),
        )
    )

    return np.mod(azimuth + 360, 360)  # Normalize to [0, 360)
