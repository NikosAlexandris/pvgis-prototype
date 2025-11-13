from typing import Annotated
from fastapi import HTTPException

from pvgisprototype.api.position.models import (
    ShadingModel,
)
from pvgisprototype.web_api.fastapi.parameters import fastapi_query_shading_model


async def process_shading_model(
    shading_model: Annotated[
        ShadingModel, fastapi_query_shading_model
    ] = ShadingModel.pvgis,
):
    NOT_IMPLEMENTED = [
        ShadingModel.all,
        ShadingModel.pvlib,
    ]

    if shading_model in NOT_IMPLEMENTED:
        raise HTTPException(
            status_code=400,
            detail=f"Option '{shading_model.name}' is not currently supported!",
        )

    return shading_model
