#from devtools import debug
#from typing import Optional
#from typing import List
from pydantic import BaseModel
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
#from fastapi import Query
#from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import ORJSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.openapi.utils import get_openapi
from jinja2 import Template

from pvgisprototype.web_api.input_parameters import FASTAPI_INPUT_PARAMETERS
from pvgisprototype.web_api.performance.broadband import get_photovoltaic_performance_analysis
from pvgisprototype.web_api.series.select import select
# from pvgisprototype.web_api.position.overview import get_calculate_solar_position_overview
# from pvgisprototype.web_api.position.solar_time import get_calculate_solar_time
# from pvgisprototype.web_api.position.overview_series import overview_series
from pvgisprototype.web_api.power.broadband import get_photovoltaic_power_series
from pvgisprototype.web_api.power.broadband import get_photovoltaic_power_series_monthly_average
from pvgisprototype.web_api.power.broadband import get_photovoltaic_power_series_advanced
# from pvgisprototype.plot.plot_solar_declination import plot_solar_declination_one_year_bokeh
# from pvgisprototype.web_api.plot.plot_example import plot_example
# from pvgisprototype.web_api.plot.plot_example import graph_example
#from pvgisprototype.constants import RADIANS
from pvgisprototype.web_api.power.broadband import get_photovoltaic_power_output_series_multi
from pvgisprototype.web_api.html_variables import html_root_page, template_html

current_file = Path(__file__).resolve()
assets_directory = current_file.parent / "web_api/assets"

summary = """
PVGIS
offers open-access insights
on solar radiation ☀
and location-specific estimates of
photovoltaic performance 📈,
for various technologies 🔌🔋
over Europe & Africa 🌍, largely Asia 🌏 and the Americas 🌎.
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

app = FastAPI(
    title="PVGIS Web API",
    description=description,
    summary=summary,
    version="6",
    terms_of_service="https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/pvgis-background-information/data-protection_en",
    contact={
        "name": "PVGIS, Joint Research Centre, European Commission",
        "url": "https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/pvgis-background-information/pvgis-contact-points_en",
        "email": "JRC-PVGIS@ec.europa.eu",
    },
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
    # license_info={
    #     "name": "",
    #     "url": "",
    # },
)

def reorder_params(api_spec, endpoint_path, params_order):
    parameters_list = api_spec["paths"][endpoint_path]["get"]["parameters"]
    ordered_parameters = sorted(
        parameters_list, key=lambda x: params_order.index(x["name"])
    )
    api_spec["paths"][endpoint_path]["get"]["parameters"] = ordered_parameters
    return api_spec


def custom_openapi():
        openapi_schema = get_openapi(
            title="Some API",
            version="1.0.0",
            summary="This is a very custom OpenAPI schema",
            description="Here's a longer description of the custom **OpenAPI** schema",
            routes=app.routes,
        )
        reordered_openapi_schema = reorder_params(
            openapi_schema,
            "/calculate/power/broadband-advanced",
            FASTAPI_INPUT_PARAMETERS,
        )
        reordered_openapi_schema = reorder_params(
            openapi_schema,
            "/calculate/power/broadband",
            FASTAPI_INPUT_PARAMETERS,
        )
        reordered_openapi_schema = reorder_params(
            openapi_schema,
            "/calculate/performance/broadband",
            FASTAPI_INPUT_PARAMETERS,
        )
        app.openapi_schema = reordered_openapi_schema
        return app.openapi_schema

app.openapi = custom_openapi

app.mount("/static", StaticFiles(directory=str(assets_directory)), name="static")
templates = Jinja2Templates(directory="templates")

template = Template(template_html)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return html_root_page

# irradiance
app.get("/calculate/performance/broadband", response_class=ORJSONResponse)(get_photovoltaic_performance_analysis)
app.get("/calculate/power/broadband")(get_photovoltaic_power_series)
app.get("/calculate/power/broadband_monthly_average")(get_photovoltaic_power_series_monthly_average)
app.get("/calculate/power/broadband-advanced")(get_photovoltaic_power_series_advanced)
app.get("/calculate/power/broadband-multi")(get_photovoltaic_power_output_series_multi)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
