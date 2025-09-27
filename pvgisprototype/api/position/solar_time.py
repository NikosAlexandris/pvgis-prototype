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
from re import UNICODE
from typing import Dict, List
from zoneinfo import ZoneInfo

from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Longitude
from pvgisprototype.algorithms.milne1921.solar_time import calculate_apparent_solar_time_series_milne1921
from pvgisprototype.algorithms.noaa.solar_time import (
    calculate_true_solar_time_series_noaa,
)
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    MINUTES,
    NOT_AVAILABLE,
    SOLAR_TIME_NAME,
    TIME_ALGORITHM_NAME,
    UNIT_NAME,
    VERBOSE_LEVEL_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
)
from pvgisprototype.log import log_function_call
from pvgisprototype.validation.functions import (
    ModelSolarTimeTimeSeriesInputModel,
    validate_with_pydantic,
)

from .models import SolarTimeModel


@log_function_call
@validate_with_pydantic(ModelSolarTimeTimeSeriesInputModel)
def model_solar_time_series(
    longitude: Longitude,
    # latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
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

    if solar_time_model.value == SolarTimeModel.milne:
        pass

        solar_time_series = calculate_apparent_solar_time_series_milne1921(
            longitude=longitude,
            timestamps=timestamps,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
        )

    if solar_time_model.value == SolarTimeModel.pvgis:
        # Requires : time_offset_global, hour_offset
        pass

    if solar_time_model.value == SolarTimeModel.noaa:

        solar_time_series = calculate_true_solar_time_series_noaa(
            longitude=longitude,
            timestamps=timestamps,
            timezone=timezone,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            validate_output=validate_output,
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
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return solar_time_series


def calculate_solar_time_series(
    longitude: Longitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_time_models: List[SolarTimeModel] = [SolarTimeModel.noaa],
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = VERBOSE_LEVEL_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
) -> Dict:
    """Calculates the solar time using all models and returns the results in a table.

    Parameters
    ----------

    Returns
    -------

    """
    results = {}
    # solar_time_models = select_models(SolarTimeModel, solar_time_model)  # Using a callback fails!
    for solar_time_model in solar_time_models:
        if (
            solar_time_model != SolarTimeModel.all
        ):  # ignore 'all' in the enumeration
            solar_time_series = model_solar_time_series(
                longitude=longitude,
                timestamps=timestamps,
                timezone=timezone,
                solar_time_model=solar_time_model,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                validate_output=validate_output,
            )
            solar_time_model_overview = {
                solar_time_model.name: {
                    TIME_ALGORITHM_NAME: (
                        solar_time_model.value if solar_time_model else NOT_AVAILABLE
                    ),
                    SOLAR_TIME_NAME: (
                        solar_time_series if solar_time_series else NOT_AVAILABLE
                    ),
                    UNIT_NAME: MINUTES,
                }
            }
            results = results | solar_time_model_overview

    return results
