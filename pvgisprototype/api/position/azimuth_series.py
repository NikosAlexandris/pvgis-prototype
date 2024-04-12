from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from typing import Optional
from typing import List
from typing import Union
from typing import Sequence
from pandas import DatetimeIndex
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.algorithms.noaa.solar_azimuth import calculate_solar_azimuth_time_series_noaa
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import ModelSolarAzimuthTimeSeriesInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype import SolarAzimuth
from pvgisprototype import RefractedSolarZenith
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from rich import print


@log_function_call
@cached(cache={}, key=custom_hashkey)
@validate_with_pydantic(ModelSolarAzimuthTimeSeriesInputModel)
def model_solar_azimuth_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex,
    timezone: ZoneInfo,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: Optional[RefractedSolarZenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
) -> SolarAzimuth:
    """
    """
    if solar_position_model.value == SolarPositionModel.noaa:

        solar_azimuth_series = calculate_solar_azimuth_time_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            dtype=dtype,
            backend=array_backend,
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
        pass

    if solar_position_model.value  == SolarPositionModel.pvlib:
        pass

    log_data_fingerprint(
            data=solar_azimuth_series.value,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return solar_azimuth_series
