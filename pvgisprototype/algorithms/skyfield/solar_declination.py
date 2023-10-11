import skyfield
from pvgisprototype.validation.functions import validate_with_pydantic
from datetime import datetime
from pvgisprototype.validation.functions import CalculateSolarDeclinationSkyfieldInput
from pvgisprototype import SolarDeclination


# NOTE gounaol: Skyfield solar declination is also computed by skyfield.solar_geometry.calculate_hour_angle_skyfield()

@validate_with_pydantic(CalculateSolarDeclinationSkyfieldInput)
def calculate_solar_declination_skyfield(      # NOTE gounaol: Declination is also calculated by skyfield.solar_geometry.calculate_hour_angle_skyfield
    timestamp: datetime,
) -> SolarDeclination:
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

    solar_declination = SolarDeclination(
        value = solar_declination.degrees,
        unit = 'degrees'
    )
    return solar_declination
