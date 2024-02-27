def test_calculate_optical_air_mass_time_series():
    elevations = np.array([1000.0, 1100.0, 1200.0])
    refracted_solar_altitudes = np.array([0.5, 0.6, 0.7])  # in radians
    
    results = calculate_optical_air_mass_time_series(elevations, refracted_solar_altitudes)
    
    # Perform your assertions here. For example, assuming optical air mass decreases with elevation:
    assert len(results) == len(elevations)
    assert np.all(np.diff(results) < 0)
