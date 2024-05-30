from datetime import datetime
from math import isfinite
from pandas import DatetimeIndex
import pvlib
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import CalculateSolarDeclinationSeriesPVLIBInput
from pvgisprototype import SolarDeclination
from pvgisprototype.constants import RADIANS
from cachetools import cached
from pvgisprototype.caching import custom_hashkey


@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(CalculateSolarDeclinationSeriesPVLIBInput)
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
