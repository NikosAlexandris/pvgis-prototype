from datetime import datetime
from typing import Any, Dict, Type, Union, get_args, get_origin, get_type_hints

from pydantic import BaseModel

from .schemas import (
    AdvancedPhotovoltaicPerformanceModel,
    ExtendedPhotovoltaicPerformanceModel,
    MinimalPhotovoltaicPerformanceModel,
    SimplePhotovoltaicPerformanceModel,
)


def unwrap_optional(annotation: Any) -> Any:
    """Unwrap Optional[T] to T if necessary."""
    if get_origin(annotation) is Union:
        return next(
            (arg for arg in get_args(annotation) if arg is not type(None)), annotation
        )
    return annotation


def get_default_for_type(annotation: Any) -> Any:
    """Return a basic default value based on type."""
    if annotation is str:
        return ""
    if annotation in (int, float):
        return 0
    if annotation is bool:
        return False
    if annotation is datetime:
        return datetime.min
    if get_origin(annotation) is list:
        return []
    if get_origin(annotation) is dict or annotation is dict:
        return {}
    return None


def generate_openapi_example(model: Type[BaseModel]) -> dict:
    """Recursively build a dummy OpenAPI example from a (optionaly nested) Pydantic model."""
    data = {}
    for name, field in get_type_hints(model, include_extras=True).items():
        annotation = unwrap_optional(field)
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            nested = generate_openapi_example(annotation)
            data[name] = annotation.model_construct(**nested)
        else:
            data[name] = get_default_for_type(annotation)
    return model.model_construct(**data).model_dump(by_alias=True, exclude_unset=False)  # type: ignore[arg-type]


def generate_openapi_examples_from_models(models: list[Type[BaseModel]]) -> dict:
    """Generate OpenAPI examples for a list of Pydantic models."""
    return {
        model.model_config.get("title", model.__name__): {
            "summary": model.model_config.get("title", model.__name__),
            "value": generate_openapi_example(model),
        }
        for model in models
    }


example_HTTP_400 = {
    "description": "**⚠️ Bad Request**. Something went wrong with your request.",
    "content": {"application/json": {"example": {"detail": "Invalid parameters"}}},
}

example_HTTP_404 = {
    "description": "**👻 Not Found**. The requested resource was not found.",
    "content": {"application/json": {"example": {"error": "Not Found"}}},
}

example_HTTP_422 = {
    "description": "**🧮 Validation Error**. The input data did not meet the required format or constraints.",
    "content": {
        "application/json": {
            "example": {
                "detail": [{"loc": ["string", 0], "msg": "string", "type": "string"}]
            }
        }
    },
}

example_HTTP_429 = {
    "description": "**🐢 Too Many Requests**. The rate limit has been exceeded.",
    "content": {"application/json": {"example": {"error": "Too Many Requests"}}},
}

example_HTTP_500 = {
    "description": "**💥 Internal Server Error**. If the issue persists, send a [help ticket](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype).",
    "content": {"application/json": {"example": {"error": "Internal Server Error"}}},
}

performance_broadband_examples_HTTP_200 = {
    "content": {
        "application/json": {
            "schema": {},  # Schema is inferred from response_model
            "examples": generate_openapi_examples_from_models(
                [
                    MinimalPhotovoltaicPerformanceModel,
                    SimplePhotovoltaicPerformanceModel,
                    AdvancedPhotovoltaicPerformanceModel,
                    ExtendedPhotovoltaicPerformanceModel,
                ]
            ),
        },
        "image/png": {
            "schema": {"type": "string", "format": "binary"},
            "example": "No example is available of PNG graphics. The response is a downloadable file",
            "description": "Quick response code image returned as PNG graphics. The response is a downloadable file",
        },
        "text/csv": {
            "schema": {"type": "string", "format": "csv"},
            "description": "Results in CSV file format. The response is a downloadable file.",
            "example": (
                "Time,Latitude,Longitude,Power ⌁,Photovoltaic Module Type,Technology,Peak Power,Peak Power Unit,"
                "Power model ⌁,Power ⌁ without Loss,Efficiency %,System Efficiency %,Global ⭍,Direct ⭍,Diffuse ⭍,"
                "Reflected ⭍,Spectral effect ±,Spectral effect ± ％,Spectral factor *,Reflectivity -,Direct Reflectivity -,"
                "Diffuse Reflectivity -,Reflected Reflectivity -,Global ∡,Direct ∡,Diffuse ∡,Reflected ∡,Global ∡ ☉,"
                "Direct ∡ ☉,Diffuse ∡ ☉,Reflected ∡ ☉,Direct Irradiance ⭳,Diffuse ⭳,Temperature ℃,Wind Speed ㎧,"
                "Surface Orientation ↻,Surface Tilt ∡,Shading 🮞,In-shade 🮞,Unit,Incidence algorithm,Incidence angle,"
                "Azimuth Origin 󱦥,Positioning ⯐,Timing ⏲,Solar constant,Perigee,Eccentricity\n"
                "2013-06-01T12:00:00.000000,45.812,8.628,468.56696,Mono-Facial,cSi:Free standing,1.0,㎾p,Huld 2011,"
                "544.8453,0.915069,0.86,544.8453,164.80295,364.56702,15.475274,0.0,0.0,1.0,-4.9331055,0.99579394,"
                "0.98963577,0.0,595.4144,180.09894,398.40387,16.911592,601.6246,180.85965,402.57626,18.188671,178.0,"
                "443.0,22.13,0.35,180.0,45.0,PVGIS,false,degrees,Iqbal,Sun-Vector-to-Surface-Plane,North,NOAA,NOAA,"
                "1360.8,0.048869,0.03344\n"
                "2013-06-01T13:00:00.000000,45.812,8.628,595.2526,Mono-Facial,cSi:Free standing,1.0,㎾p,Huld 2011,"
                "692.15424,0.89636177,0.86,692.15424,428.89777,244.60686,18.649601,0.0,0.0,1.0,-5.601837,0.9942981,"
                "0.98963577,0.0,772.18176,478.48734,272.88855,20.805885,779.35474,481.23126,275.74646,22.377043,485.0,"
                "279.0,22.3,0.45,180.0,45.0,PVGIS,false,degrees,Iqbal,Sun-Vector-to-Surface-Plane,North,NOAA,NOAA,"
                "1360.8,0.048869,0.03344"
            ),
        },
    },
    "description": "**✅ Successful execution**. The output results depends on the selected analysis level."
}
