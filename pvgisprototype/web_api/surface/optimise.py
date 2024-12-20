from typing import Annotated
from urllib.parse import quote

from fastapi import Depends
from fastapi.responses import ORJSONResponse

from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerModeWithoutNone,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.web_api.dependencies import (
    fastapi_dependable_angle_output_units,
    process_optimise_surface_position,
)
from pvgisprototype.web_api.fastapi_parameters import (
    fastapi_query_csv,
    fastapi_query_optimise_surface_position,
)
from pvgisprototype.web_api.schemas import AngleOutputUnit


async def get_optimised_surface_position(
    optimise_surface_position: Annotated[
        SurfacePositionOptimizerModeWithoutNone, fastapi_query_optimise_surface_position
    ],
    optimised_surface_position: Annotated[
        dict, Depends(process_optimise_surface_position)
    ],
    angle_output_units: Annotated[
        AngleOutputUnit, fastapi_dependable_angle_output_units
    ] = AngleOutputUnit.RADIANS,
    csv: Annotated[str | None, fastapi_query_csv] = None,
):
    if csv:
        from fastapi.responses import StreamingResponse

        csv_content = ",".join(["Surface Orientation", "Surface Tilt"]) + "\n"
        csv_content += f"{convert_float_to_degrees_if_requested(optimised_surface_position['surface_orientation'].value, angle_output_units)},{convert_float_to_degrees_if_requested(optimised_surface_position['surface_tilt'].value, angle_output_units)}"

        response_csv = StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={quote(csv)}"},
        )

        return response_csv

    response: dict = {}
    headers = {
        "Content-Disposition": 'attachment; filename="SURFACE_POSITION_OPTIMISATION.json"'
    }

    response["Surface Optimised Position"] = {
        "Optimised surface orientation": convert_float_to_degrees_if_requested(
            optimised_surface_position["surface_orientation"].value, angle_output_units
        ),
        "Optimised surface tilt": convert_float_to_degrees_if_requested(
            optimised_surface_position["surface_tilt"].value, angle_output_units
        ),
    }

    return ORJSONResponse(response, headers=headers, media_type="application/json")
