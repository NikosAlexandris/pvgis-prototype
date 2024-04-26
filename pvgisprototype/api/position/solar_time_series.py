from devtools import debug
from typing import Union
from typing import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo
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
    timestamps: Union[datetime, Sequence[datetime]],
    timezone: ZoneInfo = None,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
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
    # if local and timestamp is not None and timezone is not None:
    #     timestamp = timezone.localize(timestamp)
    if solar_time_model.value == SolarTimeModel.milne:

        pass

    if solar_time_model.value == SolarTimeModel.ephem:

        pass

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

    return solar_time_series
