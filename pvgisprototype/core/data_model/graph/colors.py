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
import colorsys
import hashlib


def generate_color_from_path(path: str, max_levels: int = 10):
    """
    Generate a visually distinct color for a given path.
    - Root component determines the base hue.
    - Each subpath level modifies saturation and lightness.
    """
    components = path.split("/")
    root = components[0]

    # Generate a consistent base hue from root
    hash_obj = hashlib.md5(root.encode())
    hue = int(hash_obj.hexdigest(), 16) / (16**32)  # Normalize to [0,1]

    # Lighter base lightness and subtle contrast with depth
    base_lightness = 0.85
    lightness = base_lightness - 0.02 * min(len(components), max_levels)

    # Slightly increase saturation with depth for contrast
    saturation = 0.4 + 0.03 * min(len(components), max_levels)

    # Convert to RGB
    r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
    return (r, g, b)
