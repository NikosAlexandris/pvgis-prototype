def calculate_optical_air_mass(sun_geometry):
    """
    Calculate the optical air mass based on sun geometry variables.

    Parameters
    ----------
    sun_geometry : dict
        Dictionary containing sun geometry variables.
        Requires the following keys:
        - 'solar_altitude' : float
            Solar altitude angle in radians.

    Returns
    -------
    float
        Calculated optical air mass.
    """
    solar_altitude = sun_geometry['solar_altitude']
    elevation_correction = np.exp(-sun_geometry['z_orig'] / 8434.5)
    correction_numerator = 0.1594 + solar_altitude * (1.123 + 0.065656 * solar_altitude)
    correction_denominator = 1. + solar_altitude * (28.9344 + 277.3971 * solar_altitude)
    atmospheric_refraction_angular_correction = 0.061359 * correction_numerator / correction_denominator  # in radians
    corrected_solar_altitude = solar_altitude + atmospheric_refraction_angular_correction
    denominator = np.sin(corrected_solar_altitude) + 0.50572 * np.power(corrected_solar_altitude * np.degrees + 6.07995, -1.6364)
    optical_air_mass = elevation_correction / denominator

    return optical_air_mass


def calculate_air_mass2_linke(solar_radiation_variables):
    """
    Calculate the air mass 2 Linke factor based on solar radiation variables.

    Parameters
    ----------
    solar_radiation_variables : dict
        Dictionary containing solar radiation variables.
        Requires the following keys:
        - 'linke' : float
            Linke turbidity factor.

    Returns
    -------
    float
        Calculated air mass 2 Linke factor.
    """
    return 0.8662 * solar_radiation_variables['linke']


def calculate_rayleigh_factor(optical_air_mass):
    """
    Calculate the Rayleigh scattering factor based on the optical air mass.

    Parameters
    ----------
    optical_air_mass : float
        Optical air mass.

    Returns
    -------
    float
        Calculated Rayleigh scattering factor.
    """
    if optical_air_mass <= 20.:
        rayleigh = 1. / (
                6.6296 + optical_air_mass * (
                    1.7513 + optical_air_mass * (
                        -0.1202 + optical_air_mass * (0.0065 - optical_air_mass * 0.00013)
                        )
                    )
                )
    else:
        rayleigh = 1. / (10.4 + 0.718 * optical_air_mass)

    return rayleigh


def calculate_direct_radiation_coefficient(
        beam_radiation_coefficient,
        extraterrestrial_direct_normal_irradiance,
        sine_of_solar_altitude,
        rayleigh,
        optical_air_mass,
        air_mass2_linke
    ):
    """
    Calculate the beam radiation coefficient.

    Parameters
    ----------
    beam_radiation_coefficient : float
        Coefficient representing the beam radiation.
    extraterrestrial_direct_normal_radiation : float
        Extraterrestrial direct normal radiation.
    sin_solar_altitude : float
        Sine of the solar altitude angle.
    rayleigh : float
        Rayleigh scattering factor.
    optical_air_mass : float
        Optical air mass.
    air_mass2_linke : float
        Air mass 2 Linke factor.

    Returns
    -------
    float
        Calculated beam radiation coefficient.
    """
    beam_radiation_coefficient =

     extraterrestrial_direct_normal_radiation * sin_solar_altitude * np.exp(-rayleigh * optical_air_mass * air_mass2_linke
    )
    return beam_radiation_coefficient


def calculate_horizontal_direct_radiation(
        horizontal_beam_radiation,
        surface_azimuth,
        surface_tilt,
        solar_constant,
        sine_of_solar_altitude,
    ):
    """
    Calculate the beam radiation.

    Parameters
    ----------
    horizontal_beam_radiation : float
        Beam radiation coefficient.
    use_efficiency : float
        Efficiency factor for converting solar radiation to usable energy.
    wind_speed : float
        Wind speed in meters per second.
    sin_solar_altitude : float
        Sine of the solar altitude angle.
    surface_geometry : dict
        Dictionary containing surface geometry variables.
        Requires the following keys:
        - 'aspect' : float
            Aspect angle of the surface.
        - 'slope' : float
            Slope angle of the surface.

    Returns
    -------
    float
        Calculated beam radiation.
    """


    if surface_azimuth is not None and surface_tilt != 0:
        surface_direct_radiation = horizontal_direct_radiation * solar_constant  / sine_of_solar_altitude
        return surface_direct_radiation

    else:
        return horizontal_direct_radiation


# from: rsun_standalone_hourly_opt.cpp
# function name: brad
def calculate_direct_radiation(
        use_efficiency,
        wind_speed,
        solar_constant,
        sun_geometry,
        surface_geometry,
        solar_radiation_variables,
        grid_geometry,
        horizon_heights,
        hour_radiation_values
):
    """
    Calculate the beam radiation for a specific moment in time considering variables like efficiency, wind speed, solar constant, sun geometry, surface geometry, solar radiation variables, grid geometry, and horizon heights.

    Parameters
    ----------
    use_efficiency : float
        Efficiency factor for converting solar radiation to usable energy.
    wind_speed : float
        Wind speed in meters per second.
    solar_constant : float
        Solar constant value representing the extraterrestrial solar radiation.
    sun_geometry : dict
        Dictionary containing sun geometry variables.
        Requires the following keys:
        - 'altitude' : float
            Solar altitude angle in radians.
    surface_geometry : dict
        Dictionary containing surface geometry variables.
        Requires the following keys:
        - 'aspect' : float
            Aspect angle of the surface.
        - 'slope' : float
            Slope angle of the surface.
    solar_radiation_variables : dict
        Dictionary containing solar radiation variables.
        Requires the following keys:
        - 'beam_radiation_coefficient' : float
            Coefficient representing the beam radiation.
        - 'extraterrestrial_direct_normal_radiation' : float
            Normal extraterrestrial radiation.
        - 'linke' : float
            Linke turbidity factor.
    grid_geometry : dict
        Dictionary containing grid geometry variables.
    horizon_heights : ndarray
        Array of horizon heights.
    hour_radiation_values : ndarray
        Array to store the calculated radiation values.

    Returns
    -------
    float
        Calculated beam radiation.
    """

    optical_air_mass = calculate_optical_air_mass(sun_geometry)
    air_mass2_linke = calculate_air_mass2_linke(solar_radiation_variables)
    rayleigh = calculate_rayleigh(optical_air_mass)

    horizontal_beam_radiation = calculate_horizontal_beam_radiation(
        solar_radiation_variables['beam_radiation_coefficient'],
        solar_radiation_variables['extraterrestrial_direct_normal_irradiance'],
        np.sin(sun_geometry['solar_altitude']),
        rayleigh,
        optical_air_mass,
        air_mass2_linke
    )

    surface_azimuth = sun_geometry['azimuth']
    surface_tilt = sun_geometry['tilt']
    sine_of_solar_altitude = sun_geometry['sine_of_solar_altitude']
    sine_of_solar_altitude = sin(sun_geometry['solar_altitude']),

    surface_beam_radiation = calculate_surface_direct_radiation(
        horizontal_beam_radiation,
        surface_azimuth,
        surface_tilt,
        solar_constant,
        sine_of_solar_altitude,
        surface_geometry
    )

    hour_radiation_values[0] = surface_beam_radiation * solar_constant * grid_geometry['area']

    return surface_beam_radiation
