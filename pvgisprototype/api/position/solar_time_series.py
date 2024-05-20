from devtools import debug
from typing import Union
from typing import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo

from pandas import DatetimeIndex
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarTimeTimeSeriesInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from .models import SolarTimeModel
from pvgisprototype.algorithms.noaa.solar_time import calculate_true_solar_time_time_series_noaa
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.log import log_function_call


@log_function_call
@validate_with_pydantic(ModelSolarTimeTimeSeriesInputModel)
def model_solar_time_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo = ZoneInfo('UTC'),
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """Calculates the solar time using the requested _algorithm_.

    Parameters
    ----------
    input : SolarTimeInput

    Returns
    -------
    SolarTime
    """
    solar_time_series = None

    # if local and timestamp is not None and timezone is not None:
    #     timestamp = timezone.localize(timestamp)
    if solar_time_model.value == SolarTimeModel.milne:

        pass

        # solar_time = calculate_apparent_solar_time_milne1921(
        #     longitude=longitude,
        #     timestamp=timestamp,
        #     verbose=verbose,
        # )

    if solar_time_model.value == SolarTimeModel.ephem:

        pass

        # solar_time = calculate_solar_time_ephem(
        #     longitude=longitude,
        #     latitude=latitude,
        #     timestamp=timestamp,
        #     timezone=timezone,
        #     verbose=verbose,
        # )

    if solar_time_model.value == SolarTimeModel.pvgis:

        # Requires : time_offset_global, hour_offset

        pass

    if solar_time_model.value == SolarTimeModel.noaa:

        solar_time_series = calculate_true_solar_time_time_series_noaa(
            longitude=longitude,
            timestamps=timestamps,
            timezone=timezone,
            verbose=verbose,
        )

    if solar_time_model.value == SolarTimeModel.skyfield:

        pass

        # # vvv vvv vvv --------------------------------------- expects degrees!
        # solar_time = calculate_solar_time_skyfield(
        #     longitude=longitude,
        #     latitude=latitude,
        #     timestamp=timestamp,
        #     timezone=timezone,
        #     verbose=verbose,
        # )
        # # ^^^ ^^^ ^^^ --------------------------------------- expects degrees!

    return solar_time_series


def calculate_solar_time_series(
        ):
    """
    """
    pass
#     longitude: Longitude,
#     latitude: Latitude,
#     timestamp: datetime,
#     timezone: ZoneInfo,
#     solar_time_models: List[SolarTimeModel] = [SolarTimeModel.skyfield],
#     perigee_offset: float = PERIGEE_OFFSET,
#     eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
#     verbose: int = 0,
# ) -> List:
#     """Calculates the solar time using all models and returns the results in a table.

#     Parameters
#     ----------
    
#     Returns
#     -------

#     """
#     results = []
#     solar_time_models = select_models(SolarTimeModel, solar_time_models)  # Using a callback fails!
#     for solar_time_model in solar_time_models:
#         solar_time = model_solar_time(
#             longitude=longitude,
#             latitude=latitude,
#             timestamp=timestamp,
#             timezone=timezone,
#             solar_time_model=solar_time_model,
#             perigee_offset=perigee_offset,
#             eccentricity_correction_factor=eccentricity_correction_factor,
#             verbose=verbose,
#         )
#         results.append({
#             TIME_ALGORITHM_NAME: solar_time_model.value,
#             SOLAR_TIME_NAME: solar_time,
#         })

#     return results
