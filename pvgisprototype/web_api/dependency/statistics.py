from typing import Annotated
from pvgisprototype.web_api.schemas import (
    GroupBy,
)
from pvgisprototype.web_api.dependency.time import process_time_grouping
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_groupby,
)


async def process_groupby(
    groupby: Annotated[GroupBy, fastapi_query_groupby] = GroupBy.NoneValue,
) -> str | None:
    return await process_time_grouping(groupby)
