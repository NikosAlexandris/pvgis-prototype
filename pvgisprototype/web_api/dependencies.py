import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from fastapi import Query, HTTPException
from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.api.utilities.timestamp import generate_datetime_series
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone


async def process_series_timestamp(
    timestamps: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    frequency: Optional[str] = Query('h')
):
    if start_time and end_time:
        try:
            generated_timestamps = generate_datetime_series(start_time, end_time, frequency)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        return generated_timestamps

    elif timestamps:
        try:
            timestamps = timestamps.strip().split(",")
            parsed_timestamps = pd.to_datetime(timestamps, format='%Y-%m-%d %H:%M:%S')
            parsed_timestamps = [ts.to_pydatetime() for ts in parsed_timestamps]
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid timestamp format")
        return parsed_timestamps

    else:
        raise HTTPException(status_code=400, detail="Either timestamps or start_time and end_time must be provided")


async def process_single_timestamp(
    timestamp: Optional[datetime] = None,
    timezone: Optional[str] = None,
)-> datetime:
    if timestamp is None:
        return now_utc_datetimezone()
    else:
        utc_zoneinfo = ZoneInfo("UTC")
        if timestamp.tzinfo != utc_zoneinfo:

            # Note the input timestamp and timezone
            user_requested_timestamp = timestamp
            user_requested_timezone = timezone

            timestamp = timestamp.astimezone(utc_zoneinfo)
            timezone = utc_zoneinfo
            print(f'Input timestamp & zone ({user_requested_timestamp} & {user_requested_timezone}) converted to {timestamp} for all internal calculations!')
        
            return timestamp
    
    
async def process_longitude(
    longitude: float = Query(..., ge=-180, le=180),
) -> float:
    return convert_to_radians_fastapi(longitude)


async def process_latitude(
    latitude: float = Query(..., ge=-90, le=90),
) -> float:
    return convert_to_radians_fastapi(latitude)


