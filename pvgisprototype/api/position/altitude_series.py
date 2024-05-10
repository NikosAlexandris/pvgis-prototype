from pvgisprototype.algorithms.jenco.solar_altitude import calculate_solar_altitude_time_series_jenco
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from typing import List, Union, Sequence
from pandas import DatetimeIndex
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarAltitude
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarAltitudeTimeSeriesInputModel
from pvgisprototype.algorithms.noaa.solar_altitude import calculate_solar_altitude_time_series_noaa
from pvgisprototype.algorithms.jenco.solar_altitude import calculate_solar_altitude_time_series_jenco
from pvgisprototype.caching import custom_hashkey
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import TIME_ALGORITHM_NAME
from pvgisprototype.constants import POSITION_ALGORITHM_NAME
from pvgisprototype.constants import ALTITUDE_NAME
from pvgisprototype.constants import UNITS_NAME
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.constants import RADIANS
from cachetools import cached
from rich import print


@log_function_call
@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(ModelSolarAltitudeTimeSeriesInputModel)
def model_solar_altitude_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    apply_atmospheric_refraction: bool = True,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = 0,
    log: int = 0,
) -> SolarAltitude:
    """
    """
    solar_altitude_series = None
    if solar_position_model.value == SolarPositionModel.noaa:

        solar_altitude_series = calculate_solar_altitude_time_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )

    if solar_position_model.value == SolarPositionModel.skyfield:
        pass

    if solar_position_model.value == SolarPositionModel.suncalc:
        pass

    if solar_position_model.value == SolarPositionModel.pysolar:
        pass

    if solar_position_model.value  == SolarPositionModel.pvis:

        solar_altitude_series = calculate_solar_altitude_time_series_jenco(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            dtype=dtype,
            array_backend=array_backend,
            verbose=0,
            log=log,
        )

    if solar_position_model.value  == SolarPositionModel.pvlib:
        pass

    return solar_altitude_series


@log_function_call
def calculate_solar_altitude_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_position_models: List[SolarPositionModel] = [SolarPositionModel.skyfield],
    solar_time_model: SolarTimeModel = SolarTimeModel.skyfield,
    apply_atmospheric_refraction: bool = True,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
) -> List:
    """
    Calculates the solar position using all models and returns the results in a table.
    """
    results = {}
    for solar_position_model in solar_position_models:
        if solar_position_model != SolarPositionModel.all:  # ignore 'all' in the enumeration
            solar_altitude_series = model_solar_altitude_time_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                solar_position_model=solar_position_model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
            )
            solar_position_model_overview = {
                    solar_position_model.name: {
                        TIME_ALGORITHM_NAME: solar_altitude_series.timing_algorithm if solar_altitude_series else NOT_AVAILABLE,
                        POSITION_ALGORITHM_NAME: solar_position_model.value,
                        ALTITUDE_NAME: getattr(solar_altitude_series, angle_output_units, NOT_AVAILABLE) if solar_altitude_series else NOT_AVAILABLE,
                        UNITS_NAME: None,
                        }
                    }
            results = results | solar_position_model_overview

    return results
