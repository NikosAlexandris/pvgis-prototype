from datetime import datetime
from typing import List, Optional

from fastapi import Depends, Query

from pvgisprototype.api.position.models import (
    SolarPositionModel,
    SolarTimeModel,
    select_models,
)
from pvgisprototype.api.position.overview import (
    calculate_solar_position_overview_series,
)
from pvgisprototype.constants import (
    ECCENTRICITY_CORRECTION_FACTOR,
    PERIGEE_OFFSET,
    RADIANS,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.web_api.dependencies import (
    process_latitude,
    process_longitude,
    process_single_timestamp,
)


async def get_calculate_solar_position_overview(
    longitude: float = Depends(process_longitude),
    latitude: float = Depends(process_latitude),
    timestamp: datetime | None = Depends(process_single_timestamp),
    timezone: str | None = Query(None),
    solar_position_models: List[SolarPositionModel] = Query(
        [SolarPositionModel.skyfield]
    ),
    apply_atmospheric_refraction: bool = Query(True),
    solar_time_model: SolarTimeModel = Query(SolarTimeModel.skyfield),
    perigee_offset: float = Query(PERIGEE_OFFSET),
    eccentricity_correction_factor: float = Query(ECCENTRICITY_CORRECTION_FACTOR),
    angle_output_units: str = Query(RADIANS),
    rounding_places: int | None = Query(5),
    verbose: int = Query(VERBOSE_LEVEL_DEFAULT),
):
    """ """
    solar_position_models = select_models(
        SolarPositionModel, solar_position_models
    )  # Using a callback fails!
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
