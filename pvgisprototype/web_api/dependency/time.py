from fastapi import Depends
from typing import Annotated, Dict, TypeVar
from zoneinfo import ZoneInfo

from pandas import Timestamp

from pvgisprototype.api.datetime.timezone import generate_a_timezone, parse_timezone
from pvgisprototype.constants import (
    TIMEZONE_UTC,
)
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_end_time,
    fastapi_query_start_time,
    fastapi_query_timezone,
    fastapi_query_timezone_to_be_converted,
    fastapi_query_frequency,
)
from pvgisprototype.web_api.schemas import (
    Frequency,
    GroupBy,
    Timezone,
)


def process_timezone(
    timezone: Annotated[Timezone, fastapi_query_timezone] = Timezone.UTC,  # type: ignore[attr-defined]
) -> ZoneInfo:
    timezone = parse_timezone(timezone.value)  # type: ignore[assignment]
    return generate_a_timezone(timezone)  # type: ignore


async def process_timezone_to_be_converted(
    timezone_for_calculations: Annotated[Timezone, fastapi_query_timezone_to_be_converted] = Timezone.UTC,  # type: ignore[attr-defined]
) -> ZoneInfo:
    timezone_for_calculations = parse_timezone(timezone_for_calculations.value)  # type: ignore[assignment]
    return generate_a_timezone(timezone_for_calculations)  # type: ignore


TimeUnit = TypeVar("TimeUnit", GroupBy, Frequency)

time_groupings: Dict[str, str | None] = {
    "Yearly": "YE",
    "Seasonal": "S",
    "Monthly": "ME",
    "Weekly": "W",
    "Daily": "D",
    "Hourly": "h",
    "Minutely": "min",
    "None": None,
}


async def process_time_grouping(time_unit: TimeUnit) -> str | None:
    return time_groupings[time_unit.value]


async def process_start_time(
    start_time: Annotated[str | None, fastapi_query_start_time] = "2013-01-01",
    timezone: Annotated[Timezone, Depends(process_timezone)] = Timezone.UTC,  # type: ignore
):
    if start_time:
        if timezone:
            try:
                start_time = (
                    Timestamp(start_time, tz=timezone)
                    .tz_convert(ZoneInfo(TIMEZONE_UTC))
                    .tz_localize(None)
                )
            except Exception as exception:
                raise HTTPException(
                    status_code=400,
                    detail=str(exception),
                )
        else:
            try:
                start_time = Timestamp(start_time)
            except Exception as exception:
                raise HTTPException(
                    status_code=400,
                    detail=str(exception),
                )

    return start_time


async def process_end_time(
    end_time: Annotated[str | None, fastapi_query_end_time] = "2013-12-31",
    timezone: Annotated[Timezone, Depends(process_timezone)] = Timezone.UTC,  # type: ignore
):
    if end_time:
        if timezone:
            try:
                end_time = (
                    Timestamp(end_time, tz=timezone)
                    .tz_convert(ZoneInfo(TIMEZONE_UTC))
                    .tz_localize(None)
                )
            except Exception as exception:
                raise HTTPException(
                    status_code=400,
                    detail=str(exception),
                )
        else:
            try:
                end_time = Timestamp(end_time)
            except Exception as exception:
                raise HTTPException(
                    status_code=400,
                    detail=str(exception),
                )

    return end_time


async def process_frequency(
    frequency: Annotated[Frequency, fastapi_query_frequency] = Frequency.Hourly,
) -> str:
    return await process_time_grouping(frequency)  # type: ignore
