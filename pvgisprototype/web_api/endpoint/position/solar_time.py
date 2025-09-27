from pvgisprototype.web_api.caching_redis import USE_REDIS_CACHE
from pvgisprototype.web_api.caching_redis import custom_cached
from pvgisprototype.log import logger
from datetime import datetime

from fastapi import Query

from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.solar_time import calculate_solar_time_series
from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.api.utilities.timestamp import convert_to_timezone


@custom_cached
async def get_calculate_solar_time(
    longitude: float = Query(..., ge=-180, le=180),
    latitude: float = Query(..., ge=-90, le=90),
    timestamps: datetime | None = None,
    timezone: str | None = None,
    model: List[SolarTimeModel] = Query(
        [SolarTimeModel.skyfield], description="Model to calculate solar time"
    ),
):

    logger.info(f"🔧 Endpoint starting - USE_REDIS_CACHE: {USE_REDIS_CACHE}")
    
    longitude = convert_to_radians_fastapi(longitude)
    latitude = convert_to_radians_fastapi(latitude)

    solar_time = calculate_solar_time_series(
        longitude=longitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_time_models=model,
    )

    return {"Local solar time": solar_time}
