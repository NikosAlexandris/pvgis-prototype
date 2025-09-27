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
def calculate_local_hour_angle(gast, alpha, longitude):
    """Calculate the Local Hour Angle (local_hour_angle)

    Examples
    --------
    gast_array = np.array([15.0116663, 16.08011407])
    alpha_array = np.array([14.261, 14.261])  # Example right ascension in hours
    longitude_array = np.array([77.5946, 77.5946])  # Example longitude in degrees (east)
    delta_array = np.array([23.44, 23.44])  # Example declination in degrees
    latitude_array = np.array([12.9714, 12.9714])  # Example latitude in degrees
    local_hour_angle_array = calculate_local_hour_angle(gast_array, alpha_array, longitude_array)
    """
    return (gast - alpha) * 15 + longitude
