from devtools import debug
from typing import List
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarTimeInputModel
from pvgisprototype import RefractedSolarZenith
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarTime
from .models import SolarTimeModels
from pvgisprototype.algorithms.milne1921.solar_time import calculate_apparent_solar_time_milne1921
from pvgisprototype.algorithms.pyephem.solar_time import calculate_solar_time_ephem
from pvgisprototype.algorithms.pvgis.solar_time import calculate_solar_time_pvgis
from pvgisprototype.algorithms.noaa.solar_time import calculate_apparent_solar_time_noaa
from pvgisprototype.algorithms.skyfield.solar_time import calculate_solar_time_skyfield
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import UNITS_NAME
from pvgisprototype.constants import TIME_ALGORITHM_NAME
from pvgisprototype.constants import UNITS_NAME
from pvgisprototype.constants import SOLAR_TIME_NAME
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT


@validate_with_pydantic(ModelSolarTimeInputModel)
def model_solar_time(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    solar_time_model: SolarTimeModels = SolarTimeModels.skyfield,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> datetime:
    """Calculates the solar time and returns the calculated value and the units.

    Parameters
    ----------
    input : SolarTimeInput

    Returns
    -------
    SolarTime
    """
    # if local and timestamp is not None and timezone is not None:
    #     timestamp = timezone.localize(timestamp)
    if solar_time_model.value == SolarTimeModels.milne:

        solar_time = calculate_apparent_solar_time_milne1921(
            longitude=longitude,
            timestamp=timestamp,
            timezone=timezone,
        )

    if solar_time_model.value == SolarTimeModels.ephem:

        solar_time = calculate_solar_time_ephem(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            verbose=verbose,
        )

    if solar_time_model.value == SolarTimeModels.pvgis:

        solar_time = calculate_solar_time_pvgis(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            verbose=verbose,
        )

    if solar_time_model.value == SolarTimeModels.noaa:

        solar_time = calculate_apparent_solar_time_noaa(
            longitude=longitude,
            timestamp=timestamp,
            timezone=timezone,
            verbose=verbose,
        )

    if solar_time_model.value == SolarTimeModels.skyfield:

        # vvv vvv vvv --------------------------------------- expects degrees!
        solar_time = calculate_solar_time_skyfield(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            verbose=verbose,
        )
        # ^^^ ^^^ ^^^ --------------------------------------- expects degrees!

    return solar_time


def calculate_solar_time(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo,
    solar_time_models: List[SolarTimeModels] = [SolarTimeModels.skyfield],
    time_output_units: str = "minutes",
    verbose: int = 0,
) -> List:
    """Calculates the solar time using all models and returns the results in a table.

    Parameters
    ----------
    
    Returns
    -------

    """
    results = []
    for solar_time_model in solar_time_models:
        if solar_time_model != SolarTimeModels.all:  # ignore 'all' in the enumeration
            solar_time = model_solar_time(
                longitude=longitude,
                latitude=latitude,
                timestamp=timestamp,
                timezone=timezone,
                solar_time_model=solar_time_model,
                verbose=verbose,
            )
            debug(locals())
            results.append({
                TIME_ALGORITHM_NAME: solar_time_model,
                SOLAR_TIME_NAME: solar_time,
                UNITS_NAME: time_output_units,  # Don't trust me -- Redesign Me!
            })

    return results
