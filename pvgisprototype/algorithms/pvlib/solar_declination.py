#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
import pvlib
from pandas import DatetimeIndex

from pvgisprototype import SolarDeclination
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import RADIANS
from pvgisprototype.validation.functions import (
    CalculateSolarDeclinationSeriesPVLIBInput,
    validate_with_pydantic,
)


@custom_cached
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
        solar_positioning_algorithm="pvlib (Spencer, 1971)",
        solar_timing_algorithm="pvlib",
    )
