from datetime import datetime
import pvlib
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarDeclinationPVLIBInput
from pvgisprototype import SolarDeclination
from pvgisprototype.constants import RADIANS


# @cache_result
@validate_with_pydantic(CalculateSolarDeclinationPVLIBInput)
def calculate_solar_declination_pvlib(
        timestamp: datetime,
) -> SolarDeclination:
        """Calculate the solar declination in radians"""
        doy = timestamp.timetuple().tm_yday
        solar_declination = pvlib.solarposition.declination_spencer71(doy)
        solar_declination = SolarDeclination(
                value=solar_declination,
                unit=RADIANS,
                position_algorithm='PVLIB',
                timing_algorithm='PVLIB',
        )

        return solar_declination
