from datetime import datetime
from math import isfinite
from pandas import DatetimeIndex
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
                position_algorithm='pvlib',
                timing_algorithm='pvlib',
        )
        if (
                not isfinite(solar_declination.degrees)
                or not solar_declination.min_degrees <= solar_declination.degrees <= solar_declination.max_degrees
        ):
                raise ValueError(
                f"The calculated solar declination angle {solar_declination.degrees} is out of the expected range\
                [{solar_declination.min_degrees}, {solar_declination.max_degrees}] degrees"
                )
        return solar_declination


def calculate_solar_declination_series_pvlib(
        timestamps: DatetimeIndex,
) -> SolarDeclination:
        """Calculate the solar declination in radians"""
        days_of_year = timestamps.dayofyear
        solar_declination_series = pvlib.solarposition.declination_spencer71(days_of_year)
        # solar_declination = pvlib.solarposition.declination_spencer71(doy)
        # if (
        #         not isfinite(solar_declination.degrees)
        #         or not solar_declination.min_degrees <= solar_declination.degrees <= solar_declination.max_degrees
        # ):
        #         raise ValueError(
        #         f"The calculated solar declination angle {solar_declination.degrees} is out of the expected range\
        #         [{solar_declination.min_degrees}, {solar_declination.max_degrees}] degrees"
        #         )
        return SolarDeclination(
            value=solar_declination_series.values,
            unit=RADIANS,
            position_algorithm='pvlib (Spencer, 1971)',
            timing_algorithm='pvlib',
        )
