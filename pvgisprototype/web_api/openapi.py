from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from pvgisprototype.web_api.input_parameters import FASTAPI_INPUT_PARAMETERS

tags_metadata = [
    {
        "name": "Features",
        "description": "A detailed overview of features and capabilities.",
        "externalDocs": {
            "description": "See also : PVGIS Overview",
            "url": "https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/",
        },
    },
    {
        "name": "Reference",
        "description": "References, publications and citation for PVGIS 6.",
        "externalDocs": {
            "description": "See also: PVGIS Reference",
            "url": "https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/reference/",
        },
    },
    {
        "name": "Data-Catalog",
        "description": "Data and artefacts consumed and served by PVGIS 6.",
        "externalDocs": {
            "description": "See also: PVGIS Data catalog",
            "url": "https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/reference/",
        },
    },
    {
        "name": "Performance",
        "description": "Analysis of photovoltaic performance",
        "externalDocs": {
            "description": "See also: PVGIS 6 Photovoltaic Performance",
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
    {
        "name": "TMY",
        "description": "Functions to calculate Typical Meteorological Year",
        "externalDocs": {
            "description": "See relevant documentation",
            "url": "https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/reference/comparison_pvgis_v6_vs_v52/?h=tmy#capabilities",
        },
    },
    {
        "name": "Solar-Position",
        "description": "Functions to calculate solar position time series",
        "externalDocs": {
            "description": "See relevant documentation",
            "url": "https://pvis-be-prototype-main-pvgis.apps.ocpt.jrc.ec.europa.eu/reference/solar_position/",
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
            "/power/broadband",
            FASTAPI_INPUT_PARAMETERS,
        )
        reordered_openapi_schema = reorder_parameters(
            openapi_schema,
            "/power/broadband-demo",
            FASTAPI_INPUT_PARAMETERS,
        )
        reordered_openapi_schema = reorder_parameters(
            openapi_schema,
            "/power/broadband-multiple-surfaces",
            FASTAPI_INPUT_PARAMETERS,
        )
        reordered_openapi_schema = reorder_parameters(
            openapi_schema,
            "/performance/broadband",
            FASTAPI_INPUT_PARAMETERS,
        )
        reordered_openapi_schema = reorder_parameters(
            openapi_schema,
            "/solar-position/overview",
            FASTAPI_INPUT_PARAMETERS,
        )

        app.openapi_schema = reordered_openapi_schema
        return app.openapi_schema

    return custom_openapi
