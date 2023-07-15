from typing import Optional
from datetime import datetime
from fastapi import Depends, Query
from zoneinfo import ZoneInfo

from pvgisprototype.api.geometry.noaa.solar_position_noaa import calculate_noaa_solar_position

from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import convert_to_timezone

async def noaa_solar_position(
    longitude: float = Query(..., ge=-180, le=180),
    latitude: float = Query(..., ge=-90, le=90),
    timestamp: Optional[datetime] = Query(None),
    timezone: Optional[str] = Query(None),
    refracted_solar_zenith: float = Query(1.5853349194640094),
    apply_atmospheric_refraction: Optional[bool] = Query(True),
    time_output_units: str = Query('minutes'),
    angle_units: str = Query('radians'),
    angle_output_units: str = Query('radians'),
    rounding_places: Optional[int] = Query(5),
    verbose: bool = Query(False)
):

    longitude = convert_to_radians_fastapi(longitude)
    latitude = convert_to_radians_fastapi(latitude)

    if timestamp is None:
        timestamp = now_utc_datetimezone()

    if timezone:
        timezone = convert_to_timezone(timezone)
        timestamp = timestamp.astimezone(timezone)


    solar_position_calculations = calculate_noaa_solar_position(
        longitude,
        latitude,
        timestamp,
        timezone,
        refracted_solar_zenith,
        apply_atmospheric_refraction,
        time_output_units,
        angle_units,
        angle_output_units,
    )

    # ... all the rest of your function logic

    return {"solar_position_table": solar_position_calculations}
