from datetime import datetime
from typing import List, Optional

from fastapi import Query

from pvgisprototype.api.datetime.now import now_utc_datetimezone
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.solar_time import calculate_solar_time
from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.api.utilities.timestamp import convert_to_timezone


async def get_calculate_solar_time(
    longitude: float = Query(..., ge=-180, le=180),
    latitude: float = Query(..., ge=-90, le=90),
    timestamp: datetime | None = None,
    timezone: str | None = None,
    model: List[SolarTimeModel] = Query(
        [SolarTimeModel.skyfield], description="Model to calculate solar time"
    ),
    perigee_offset: float = Query(0.048869, description="Perigee offset"),
    eccentricity_correction_factor: float = Query(0.01672, description="Eccentricity"),
    time_offset_global: float = Query(0, description="Global time offset"),
):
    longitude = convert_to_radians_fastapi(longitude)
    latitude = convert_to_radians_fastapi(latitude)

    if timestamp is None:
        timestamp = now_utc_datetimezone()

    if timezone:
        timezone = convert_to_timezone(timezone)
        timestamp = timestamp.astimezone(timezone)

    solar_time = calculate_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_time_models=model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
    )

    return {"Local solar time": solar_time}
