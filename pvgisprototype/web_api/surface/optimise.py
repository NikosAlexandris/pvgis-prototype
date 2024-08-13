from typing import Annotated
from fastapi import Depends
from fastapi.responses import ORJSONResponse
from pvgisprototype.web_api.dependencies import process_optimise_surface_position


async def get_optimised_surface_position(
        optimise_surface_position: Annotated[dict, Depends(process_optimise_surface_position)]):
    print(optimise_surface_position)
    response: dict = {}
    headers = {
        "Content-Disposition": f'attachment; filename="SURFACE_OPTIMISATION.json"'
    }

    response["Surface Position"] = {
        'surface_orientation': optimise_surface_position["surface_orientation"].value,
        'surface_tilt': optimise_surface_position["surface_tilt"].value,}

    return ORJSONResponse(response, headers=headers, media_type="application/json")
