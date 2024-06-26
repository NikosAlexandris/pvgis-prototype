from fastapi.openapi.utils import get_openapi
from pvgisprototype.web_api.input_parameters import FASTAPI_INPUT_PARAMETERS
from fastapi import FastAPI

tags_metadata = [
    {
        "name": "Welcome",
        "description": "Welcome message and similar functions.",
        "externalDocs": {
            "description": "See also : PVGIS Overview",
            "url": "https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/overview/",
        },
    },
    {
        "name": "Reference",
        "description": "References, publications and citation for PVGIS 6.",
    },
    {
        "name": "Performance",
        "description": "Analysis of photovoltaic performance",
        "externalDocs": {
            "description": "See relevant documentation",
            "url": "https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/reference/photovoltaic_performance/",
        },
    },
    {
        "name": "Power",
        "description": "Functions to calculate photovoltaic power/energy time series",
        "externalDocs": {
            "description": "See relevant documentation",
            "url": "https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/cli/power/introduction/",
        },
    },
]


def reorder_parameters(api_spec, endpoint_path, params_order):
    if "parameters" in api_spec["paths"][endpoint_path]["get"]:
        parameters_list = api_spec["paths"][endpoint_path]["get"]["parameters"]
        ordered_parameters = sorted(
            parameters_list, key=lambda x: params_order.index(x["name"])
        )
        api_spec["paths"][endpoint_path]["get"]["parameters"] = ordered_parameters
    return api_spec


def customise_openapi(app: FastAPI):
    def custom_openapi():
            if app.openapi_schema:
                return app.openapi_schema
            openapi_schema = get_openapi(
                title=app.title,
                version=app.version,
                summary=app.summary,
                description=app.description,
                routes=app.routes,
                terms_of_service=app.terms_of_service,
                contact=app.contact,
                license_info=app.license_info,
                tags=app.openapi_tags,
            )
            openapi_schema["info"]["x-logo"] = {
                "url": "http://127.0.02:8000/assets/pvgis6_70px.png",
                # "backgroundColor": "#FFFFFF",
                "altText": "PVGIS 6 logo",
            }
            reordered_openapi_schema = reorder_parameters(
                openapi_schema,
                "/calculate/power/broadband-advanced",
                FASTAPI_INPUT_PARAMETERS,
            )
            reordered_openapi_schema = reorder_parameters(
                openapi_schema,
                "/calculate/power/broadband",
                FASTAPI_INPUT_PARAMETERS,
            )
            reordered_openapi_schema = reorder_parameters(
                openapi_schema,
                "/calculate/performance/broadband",
                FASTAPI_INPUT_PARAMETERS,
            )
            app.openapi_schema = reordered_openapi_schema
            return app.openapi_schema
    return custom_openapi
