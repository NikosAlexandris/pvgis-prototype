def calculate_solar_azimuth_jenco(
):
    """ """
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    apply_atmospheric_refraction: bool,
    refracted_solar_zenith: RefractedSolarZenith,
    perigee_offset: float,
    eccentricity_correction_factor: float,
    time_offset_global: int,
    hour_offset: int,
    solar_time_model: SolarTimeModels,
) -> SolarAzimuth:
    """Compute various solar geometry variables.

    Returns
    -------
    solar_azimuth: float


    Returns
    -------
    solar_azimuth: float
    """
    solar_declination = calculate_solar_declination_pvis(
        timestamp=timestamp,
    )
    C11 = sin(latitude.radians) * cos(solar_declination.radians)
    C13 = cos(latitude.radians) * sin(solar_declination.radians)
    C22 = cos(solar_declination.radians)
    solar_time = model_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        model=solar_time_model,  # returns datetime.time object
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
    )
    hour_angle = calculate_hour_angle(solar_time=solar_time)
    tangent_solar_azimuth = (C22 * sin(hour_angle.radians)) / (
        C11 * cos(hour_angle.radians) - C13
    )
    solar_azimuth = atan(tangent_solar_azimuth)
    solar_azimuth = SolarAzimuth(value=solar_azimuth, unit=RADIANS) # zero_direction ='East'

    return solar_azimuth
