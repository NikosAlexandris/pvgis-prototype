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
