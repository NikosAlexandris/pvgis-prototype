# from typing import Optional
from datetime import datetime
import pvlib
# from ...api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarDeclinationPVLIBInput
from pvgisprototype import SolarDeclination


# @cache_result
@validate_with_pydantic(CalculateSolarDeclinationPVLIBInput)
def calculate_solar_declination_pvlib(
        timestamp: datetime,
        # angle_output_units: Optional[str] = 'radians'
) -> SolarDeclination:
        """Calculate the solar declination in radians"""
        doy = timestamp.timetuple().tm_yday
        solar_declination = pvlib.solarposition.declination_spencer71(doy)

        solar_declination = SolarDeclination(value=solar_declination, unit='radians')
        # solar_declination = convert_to_degrees_if_requested(
        #         solar_declination,
        #         angle_output_units,
        #         )
        return solar_declination
