from datetime import datetime
from fastapi import Depends, Query
from pvgisprototype.api.position.overview import calculate_solar_position_overview_series
from typing import Optional
from typing import List
from pvgisprototype.constants import RADIANS
from pvgisprototype.web_api.dependencies import process_series_timestamp
from pvgisprototype.web_api.dependencies import process_longitude
from pvgisprototype.web_api.dependencies import process_latitude
from pvgisprototype.web_api.dependencies import process_single_timestamp
from pvgisprototype.api.position.models import select_models
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR


async def get_calculate_solar_position_overview(
    longitude: float = Depends(process_longitude),
    latitude: float = Depends(process_latitude),
    timestamp: Optional[datetime] = Depends(process_single_timestamp),
    timezone: Optional[str] = Query(None),
    solar_position_models: List[SolarPositionModel] = Query([SolarPositionModel.skyfield]),
    apply_atmospheric_refraction: bool = Query(True),
    solar_time_model: SolarTimeModel = Query(SolarTimeModel.skyfield),
    perigee_offset: float = Query(PERIGEE_OFFSET),
    eccentricity_correction_factor: float = Query(ECCENTRICITY_CORRECTION_FACTOR),
    angle_output_units: str = Query(RADIANS),
    rounding_places: Optional[int] = Query(5),
    verbose: int = Query(VERBOSE_LEVEL_DEFAULT),   
):
    """ """
    solar_position_models = select_models(SolarPositionModel, solar_position_models)  # Using a callback fails!
    results = calculate_solar_position_overview_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamp,
        timezone=timezone,
        solar_position_models=solar_position_models,
        solar_time_model=solar_time_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )
    return results
