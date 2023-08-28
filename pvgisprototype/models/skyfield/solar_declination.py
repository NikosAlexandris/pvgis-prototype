import skyfield


@validate_with_pydantic(CalculateSolarDeclinationSkyfieldInputModel, expand_args=True)
def calculate_solar_declination_skyfield(
    timestamp: datetime,
):
    """Calculate the solar declination using Skyfield

    Notes
    -----

    Skyfield calculates by default coordinates in the permanent GCRS coordinate system.
    Giving the epoch value 'date' is required to express the solar declination
    in year-specific coordinates.
    """
    timescale = skyfield.api.load.timescale()
    planets = skyfield.api.load('de421.bsp')
    sun = planets['sun']
    earth = planets['earth']

    requested_timestamp = timescale.from_datetime(timestamp)
    # solar_position = calculate_solar_position_skyfield(
    #     longitude=longitude,
    #     latitude=latitude,
    #     timestamp=timestamp,
    #     timezone=timezone,
    #     angle_output_units=angle_output_units,
    # )
    solar_position = (earth).at(requested_timestamp).observe(sun).apparent()
    right_angle, solar_declination, distance_to_sun = solar_position.radec(epoch='date')

    return solar_declination
