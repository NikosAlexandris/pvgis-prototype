from typing import Annotated
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_angle_output_units
)
from pvgisprototype.constants import (
    DEGREES,
    RADIANS,
)
from pvgisprototype.web_api.schemas import (
    AngleOutputUnit,
)


async def process_angle_output_units(
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_query_angle_output_units
    ] = AngleOutputUnit.RADIANS,
) -> str:
    """ """
    if angle_output_units.value == AngleOutputUnit.RADIANS.value:
        return RADIANS
    else:
        return DEGREES
