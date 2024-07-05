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
