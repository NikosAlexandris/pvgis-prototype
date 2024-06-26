from pathlib import Path

from fastapi import FastAPI, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.responses import ORJSONResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Template

from fastapi.openapi.docs import get_swagger_ui_html

from pvgisprototype.api.citation import generate_citation_text
from pvgisprototype.web_api.performance.broadband import get_photovoltaic_performance_analysis
from pvgisprototype.web_api.power.broadband import get_photovoltaic_power_series
from pvgisprototype.web_api.power.broadband import get_photovoltaic_power_series_monthly_average
from pvgisprototype.web_api.power.broadband import get_photovoltaic_power_series_advanced
from pvgisprototype.web_api.power.broadband import get_photovoltaic_power_output_series_multi
from pvgisprototype.web_api.html_variables import html_root_page, template_html

current_file = Path(__file__).resolve()
assets_directory = current_file.parent / "web_api/assets"
static_directory = current_file.parent / "web_api/static"

summary = """
PVGIS
offers open-access insights
on :

- solar radiation ☀

- and location-specific estimates of

- photovoltaic performance 📈,

- for various technologies 🔌🔋

- over Europe & Africa 🌍, largely Asia 🌏 and the Americas 🌎.
"""

description = """
The **PVGIS Web API**
is a public service
supported by the
[Joint Research Centre (JRC)](https://joint-research-centre.ec.europa.eu/index_en)
European Commission. 🇪🇺
For detailed information and structured content,
please refer to the
[PVGIS Documentation](https://jrc-projects.apps.ocp.jrc.ec.europa.eu/pvgis/pvis-be-prototype/).
"""


from pvgisprototype.web_api.openapi import tags_metadata

app = FastAPI(
    title="PVGIS Web API",
    description=description,
    summary=summary,
    version="6",
    openapi_tags=tags_metadata,
    terms_of_service="https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/pvgis-background-information/data-protection_en",
    contact={
        "name": "PVGIS, Joint Research Centre, European Commission",
        "url": "https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/pvgis-background-information/pvgis-contact-points_en",
        "email": "JRC-PVGIS@ec.europa.eu",
    },
    license_info={
        "name": "EUPL-1.2",
        "url": "https://spdx.org/licenses/EUPL-1.2.html",
    },
    swagger_ui_parameters={
        # "syntaxHighlight.theme": "obsidian",
        "syntaxHighlight": False,
        # "defaultModelsExpandDepth": -1,  # Hide models section
        "docExpansion": "none",  # expand only tags
        "filter": True,  # filter tags
        "displayRequestDuration": True,  # Display request duration
        "showExtensions": True,  # Show vendor extensions
    },
)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root():
    return html_root_page


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_css_url="/static/custom.css",
        swagger_js_url="/static/custom.js"
    )




# app.mount("/static", StaticFiles(directory=str(assets_directory)), name="static")
app.mount("/assets", StaticFiles(directory=str(assets_directory)), name="static")
templates = Jinja2Templates(directory="templates")
template = Template(template_html)


@app.get("/welcome", tags=['Welcome'])
async def print_welcome_message():
    welcome_message = "Welcome to PVGIS 6"
    return welcome_message


@app.get("/references/license", tags=["Reference"])
async def print_license_text():
    return generate_citation_text()


@app.get("/references/citation", tags=["Reference"])
async def print_citation_text():
    return generate_citation_text()


@app.get("/references/download-citation", tags=["Reference"])
async def download_citation():
    citation = generate_citation_text()
    from fastapi.responses import FileResponse
    import tempfile
    import json

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as tmp:
        json.dump(citation, tmp, indent=4)
        tmp_path = tmp.name

    return FileResponse(
        tmp_path, media_type="application/json", filename="citation.json"
    )


@app.get("/references/publications", tags=["Reference"], response_class=FileResponse)
async def print_references():
    bibtex_file_path = assets_directory / "references.bib"
    return FileResponse(bibtex_file_path, media_type='application/x-bibtex', filename="references.bib")


app.get(
    "/calculate/performance/broadband",
    tags=["Performance"],
    response_class=ORJSONResponse,
    summary="Analysis of Photovoltaic Performance",
    response_description="Analysis of Photovoltaic Performance (JSON)",
    status_code=status.HTTP_201_CREATED,
)(get_photovoltaic_performance_analysis)
app.get("/calculate/power/broadband", tags=["Power"])(get_photovoltaic_power_series)
app.get("/calculate/power/broadband_monthly_average", tags=["Power"])(
    get_photovoltaic_power_series_monthly_average
)
app.get("/calculate/power/broadband-advanced", tags=["Power"])(
    get_photovoltaic_power_series_advanced
)
app.get("/calculate/power/broadband-multi", tags=["Power", "Multiple surfaces"])(
    get_photovoltaic_power_output_series_multi
)


from pvgisprototype.web_api.openapi import customise_openapi
app.openapi = customise_openapi(app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
