import math
from typing import Annotated, List

from pvgisprototype import (
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.api.position.models import (
    SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SolarIncidenceModel,
    SolarPositionModel,
)
from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
from pvgisprototype.constants import (
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_ORIENTATION_MAXIMUM,
    SURFACE_ORIENTATION_MINIMUM,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_MAXIMUM,
    SURFACE_TILT_MINIMUM,
)
from pvgisprototype.web_api.fastapi.parameters import (
    fastapi_query_solar_incidence_model,
    fastapi_query_solar_position_model,
    fastapi_query_solar_position_models,
    fastapi_query_surface_orientation,
    fastapi_query_surface_orientation_list,
    fastapi_query_surface_tilt,
    fastapi_query_surface_tilt_list,
)


async def process_surface_orientation(
    surface_orientation: Annotated[
        float, fastapi_query_surface_orientation
    ] = SURFACE_ORIENTATION_DEFAULT,
) -> SurfaceOrientation:
    # return SurfaceOrientation(value = convert_to_radians_fastapi(surface_orientation), unit = RADIANS) # FIXME Revert to this when pydantic objects will be created
    return convert_to_radians_fastapi(surface_orientation)


async def process_surface_tilt(
    surface_tilt: Annotated[float, fastapi_query_surface_tilt] = SURFACE_TILT_DEFAULT,
) -> SurfaceTilt:
    # return SurfaceTilt(value = convert_to_radians_fastapi(surface_tilt), unit = RADIANS) # FIXME Revert to this when pydantic objects will be created
    return convert_to_radians_fastapi(surface_tilt)


async def process_surface_tilt_list(
    surface_tilt: Annotated[list[float], fastapi_query_surface_tilt_list] = [
        float(SURFACE_TILT_DEFAULT)
    ],
    surface_orientation: Annotated[
        list[float], fastapi_query_surface_orientation_list
    ] = [float(SURFACE_ORIENTATION_DEFAULT)],
) -> list[float]:
    """ """
    for surface_tilt_value in surface_tilt:
        if not SURFACE_TILT_MINIMUM <= surface_tilt_value <= SURFACE_TILT_MAXIMUM:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=400,
                detail=f"Value {surface_tilt_value} is out of the range {SURFACE_TILT_MINIMUM}-{SURFACE_TILT_MAXIMUM}.",
            )

    if len(surface_orientation) != len(surface_tilt):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="Surface tilt options and surface orientation options must have the same number of inputs",
        )

    return [math.radians(surface_tilt_value) for surface_tilt_value in surface_tilt]


async def process_surface_orientation_list(
    surface_tilt: Annotated[list[float], fastapi_query_surface_tilt_list] = [
        float(SURFACE_TILT_DEFAULT)
    ],
    surface_orientation: Annotated[
        list[float], fastapi_query_surface_orientation_list
    ] = [float(SURFACE_ORIENTATION_DEFAULT)],
) -> list[float]:
    """ """
    for surface_orientation_value in surface_orientation:
        if (
            not SURFACE_ORIENTATION_MINIMUM
            <= surface_orientation_value
            <= SURFACE_ORIENTATION_MAXIMUM
        ):
            from fastapi import HTTPException

            raise HTTPException(
                status_code=400,
                detail=f"Value {surface_orientation_value} is out of the range {SURFACE_ORIENTATION_MINIMUM}-{SURFACE_ORIENTATION_MAXIMUM}.",
            )

    if len(surface_orientation) != len(surface_tilt):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="Surface tilt options and surface orientation options must have the same number of inputs",
        )

    return [
        math.radians(surface_orientation_value)
        for surface_orientation_value in surface_orientation
    ]


async def process_series_solar_position_model(
    solar_position_model: Annotated[
        SolarPositionModel, fastapi_query_solar_position_model
    ] = SOLAR_POSITION_ALGORITHM_DEFAULT,
) -> SolarPositionModel:
    """ """
    NOT_IMPLEMENTED_MODELS = [
        SolarPositionModel.hofierka,
        SolarPositionModel.pvlib,
        SolarPositionModel.pysolar,
        SolarPositionModel.skyfield,
        SolarPositionModel.suncalc,
        SolarPositionModel.all,
    ]
    if solar_position_model in NOT_IMPLEMENTED_MODELS:
        models_bad_choices = ", ".join(model.value for model in NOT_IMPLEMENTED_MODELS)
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail=f"Models {models_bad_choices} are currently not supported.",
        )

    return solar_position_model


async def process_series_solar_position_models_list(
    solar_position_models: Annotated[
        List[SolarPositionModel], fastapi_query_solar_position_models
    ] = [SolarPositionModel.noaa],
) -> List[SolarPositionModel]:

    NOT_IMPLEMENTED_MODELS = [
        SolarPositionModel.hofierka,
        SolarPositionModel.pvlib,
        SolarPositionModel.pysolar,
        SolarPositionModel.skyfield,
        SolarPositionModel.suncalc,
        SolarPositionModel.all,
    ]

    for solar_position_model in solar_position_models:
        if solar_position_model in NOT_IMPLEMENTED_MODELS:
            models_bad_choices = ", ".join(
                model.value for model in NOT_IMPLEMENTED_MODELS
            )

            from fastapi import HTTPException

            raise HTTPException(
                status_code=400,
                detail=f"Models {models_bad_choices} are currently not supported.",
            )

    return solar_position_models


async def process_series_solar_incidence_model(
    solar_incidence_model: Annotated[
        SolarIncidenceModel, fastapi_query_solar_incidence_model
    ] = SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
) -> SolarIncidenceModel:
    """ """
    NOT_IMPLEMENTED_MODELS = [
        SolarIncidenceModel.pvis,
        SolarIncidenceModel.all,
    ]
    if solar_incidence_model in NOT_IMPLEMENTED_MODELS:
        models_bad_choices = ", ".join(model.value for model in NOT_IMPLEMENTED_MODELS)
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail=f"Models {models_bad_choices} are currently not supported.",
        )

    return solar_incidence_model
