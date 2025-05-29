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
