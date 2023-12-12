from devtools import debug
from typing import Optional
from typing import List
from typing import Union
from typing import Sequence
from datetime import datetime
from pvgisprototype.algorithms.noaa.solar_azimuth import calculate_solar_azimuth_time_series_noaa
from pvgisprototype.validation.functions import validate_with_pydantic
# from pvgisprototype.validation.functions import ModelSolarAzimuthTimeSeriesInputModel
from pvgisprototype import Longitude
from pvgisprototype import Latitude
from pvgisprototype.api.geometry.models import SolarPositionModel
from pvgisprototype.api.geometry.models import SolarTimeModel
from pvgisprototype import SolarAzimuth
from datetime import datetime
from zoneinfo import ZoneInfo
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype import RefractedSolarZenith


# @validate_with_pydantic(ModelSolarAzimuthTimeSeriesInputModel)
def model_solar_azimuth_time_series(
    longitude: Longitude,
    latitude: Latitude,
    timestamps: Union[datetime, Sequence[datetime]],
    timezone: ZoneInfo,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: Optional[RefractedSolarZenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    solar_time_model: SolarTimeModel = SolarTimeModel.milne,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> List[SolarAzimuth]:

    if verbose > 5:
        debug(locals())

    if solar_position_model.value == SolarPositionModel.noaa:

        solar_azimuth_series = calculate_solar_azimuth_time_series_noaa(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            verbose=verbose,
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

    return solar_azimuth_series

