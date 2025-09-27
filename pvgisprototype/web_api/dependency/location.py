from typing import Annotated
from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_longitude,
    fastapi_query_latitude,
)
from pvgisprototype import (
    Latitude,
    Longitude,
)


async def process_longitude(
    longitude: Annotated[float, fastapi_query_longitude] = 8.628,
) -> Longitude:
    # return Longitude(value = convert_to_radians_fastapi(longitude), unit = RADIANS) # FIXME Revert to this when pydantic objects will be created
    return convert_to_radians_fastapi(longitude)


async def process_latitude(
    latitude: Annotated[float, fastapi_query_latitude] = 45.812,
) -> Latitude:
    # return Latitude(value = convert_to_radians_fastapi(latitude), unit = RADIANS) # FIXME Revert to this when pydantic objects will be created
    return convert_to_radians_fastapi(latitude)
