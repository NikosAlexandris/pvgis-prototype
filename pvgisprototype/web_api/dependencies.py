from fastapi import Query, HTTPException
from typing import Optional, List
from datetime import datetime
import pandas as pd
from pvgisprototype.api.utilities.timestamp import generate_datetime_series


async def process_timestamp_input(
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
