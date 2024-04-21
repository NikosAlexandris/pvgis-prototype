from devtools import debug
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarTimeInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype.api.position.models import select_models
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.algorithms.milne1921.solar_time import calculate_apparent_solar_time_milne1921
from pvgisprototype.algorithms.pyephem.solar_time import calculate_solar_time_ephem
from pvgisprototype.algorithms.pvgis.solar_time import calculate_solar_time_pvgis
from pvgisprototype.algorithms.noaa.solar_time import calculate_true_solar_time_noaa
from pvgisprototype.algorithms.skyfield.solar_time import calculate_solar_time_skyfield
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import TIME_ALGORITHM_NAME
from pvgisprototype.constants import UNITS_NAME
from pvgisprototype.constants import SOLAR_TIME_NAME


@validate_with_pydantic(ModelSolarTimeInputModel)
def model_solar_time(
    longitude: Longitude,
    latitude: Latitude,
    timestamp: datetime,
    timezone: ZoneInfo = None,
    solar_time_model: SolarTimeModel = SolarTimeModel.skyfield,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_offset_global: float = 0,
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
    if solar_time_model.value == SolarTimeModel.milne:

        solar_time = calculate_apparent_solar_time_milne1921(
            longitude=longitude,
            timestamp=timestamp,
            verbose=verbose,
        )

    if solar_time_model.value == SolarTimeModel.ephem:

        solar_time = calculate_solar_time_ephem(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            verbose=verbose,
        )

    if solar_time_model.value == SolarTimeModel.pvgis:

        solar_time = calculate_solar_time_pvgis(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_offset_global=time_offset_global,
            verbose=verbose,
        )

    if solar_time_model.value == SolarTimeModel.noaa:

        solar_time = calculate_true_solar_time_noaa(
            longitude=longitude,
            timestamp=timestamp,
            timezone=timezone,
            verbose=verbose,
        )

    if solar_time_model.value == SolarTimeModel.skyfield:

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
    solar_time_models: List[SolarTimeModel] = [SolarTimeModel.skyfield],
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_offset_global: float = 0,
    verbose: int = 0,
) -> List:
    """Calculates the solar time using all models and returns the results in a table.

    Parameters
    ----------
    
    Returns
    -------

    """
    results = []
    solar_time_models = select_models(SolarTimeModel, solar_time_models)  # Using a callback fails!
    for solar_time_model in solar_time_models:
        solar_time = model_solar_time(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            solar_time_model=solar_time_model,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_offset_global=time_offset_global,
            verbose=verbose,
        )
        results.append({
            TIME_ALGORITHM_NAME: solar_time_model.value,
            SOLAR_TIME_NAME: solar_time,
        })

    return results
