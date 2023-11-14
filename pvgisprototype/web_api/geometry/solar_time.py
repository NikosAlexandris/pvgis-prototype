from fastapi import Query
from typing import Optional
from typing import List
from pvgisprototype.api.geometry.time import calculate_solar_time
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import convert_to_timezone
from datetime import datetime
from pvgisprototype.constants import RADIANS


async def get_calculate_solar_time(
    longitude: float = Query(..., ge=-180, le=180),
    latitude: float = Query(..., ge=-90, le=90),
    timestamp: Optional[datetime] = None,
    timezone: Optional[str] = None,
    model: List[SolarTimeModels] = Query([SolarTimeModels.skyfield], description="Model to calculate solar time"),
    refracted_solar_zenith: float = Query(1.5853349194640094, description='The solar zenith angle defaults to 1.5853349194640094 radians at sunrise or sunset, adjusted for the approximate correction for atmospheric refraction at those times, and the size of the solar disk.'),
    apply_atmospheric_refraction: bool = False,
    time_output_units: Optional[str] = 'minutes',
    angle_units: Optional[str] = RADIANS,
    angle_output_units: Optional[str] = RADIANS,
    perigee_offset: float = Query(0.048869, description="Perigee offset"),
    eccentricity_correction_factor: float = Query(0.01672, description="Eccentricity"),
    time_offset_global: float = Query(0, description="Global time offset"),
    hour_offset: float = Query(0, description="Hour offset"),
):
    # debug(locals())
    longitude = convert_to_radians_fastapi(longitude)
    latitude = convert_to_radians_fastapi(latitude)

    if timestamp is None:
        timestamp = now_utc_datetimezone()

    if timezone:
        timezone = convert_to_timezone(timezone)
        timestamp = timestamp.astimezone(timezone)
    
    # debug(locals())
    solar_time  = calculate_solar_time(
            longitude=longitude,
            latitude=latitude,
            timestamp=timestamp,
            timezone=timezone,
            solar_time_models=model,
            time_output_units=time_output_units,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_offset_global=time_offset_global,
            )
    # debug(locals())
    return {"Local solar time": solar_time}



