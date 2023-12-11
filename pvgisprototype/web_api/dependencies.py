import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from fastapi import Query
from fastapi import HTTPException
from fastapi import Depends
from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import convert_to_timezone
from pvgisprototype.api.utilities.timestamp import attach_requested_timezone
from pvgisprototype.api.utilities.timestamp import parse_timestamp_series
from pvgisprototype.api.utilities.timestamp import generate_datetime_series

from pvgisprototype.web_api.fastapi_parameters import fastapi_query_longitude
from pvgisprototype.web_api.fastapi_parameters import fastapi_query_latitude
from typing import Annotated


async def process_series_timestamp(
    timestamps: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None),
    frequency: Optional[str] = Query('h'),
    end_time: Optional[str] = Query(None),
    timezone: Optional[str] = None,
):
    """
    """
    timezone = convert_to_timezone(timezone)
    from devtools import debug
    debug(locals())
    if timestamps is not None and not start_time and not end_time:
        timestamps = parse_timestamp_series(timestamps=timestamps)

    if start_time is not None and end_time is not None:
        try:
            timestamps = generate_datetime_series(
                start_time=start_time,
                frequency=frequency,
                end_time=end_time,
                timezone=timezone,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    debug(locals())
    return timestamps


async def process_single_timestamp(
    timestamp: Optional[str] = None,
    timezone: Optional[str] = None,
)-> datetime:
    if timestamp is None:
        return now_utc_datetimezone()
    else:
        from dateutil import parser
        timestamp = parser.parse(timestamp)

        from pandas import to_datetime
        timestamp = to_datetime(timestamp, errors='raise')

        timestamp = attach_requested_timezone(timestamp, timezone)
        utc_zoneinfo = ZoneInfo("UTC")
        if timestamp.tzinfo != utc_zoneinfo:

            # Note the input timestamp and timezone
            user_requested_timestamp = timestamp
            user_requested_timezone = timezone

            timestamp = timestamp.astimezone(utc_zoneinfo)
            timezone = utc_zoneinfo
            # print(f'Input timestamp & zone ({user_requested_timestamp} & {user_requested_timezone}) converted to {timestamp} for all internal calculations!')
        
        return timestamp


async def process_longitude(
    longitude: Annotated[float, fastapi_query_longitude],
) -> float:
    return convert_to_radians_fastapi(longitude)


async def process_latitude(
    latitude: Annotated[float, fastapi_query_latitude],
) -> float:
    return convert_to_radians_fastapi(latitude)


fastapi_dependable_longitude = Depends(process_longitude)
fastapi_dependable_latitude = Depends(process_latitude)
fastapi_dependable_timestamps = Depends(process_series_timestamp)
