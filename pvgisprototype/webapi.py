from devtools import debug

from typing import Optional
from typing import List
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi import Query
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from bokeh.resources import INLINE

from pvgisprototype.web_api.geometry.noaa.solar_position import get_calculate_solar_geometry_overview
from pvgisprototype.web_api.geometry.solar_time import get_calculate_solar_time
from pvgisprototype.web_api.geometry.noaa.solar_position import get_calculate_noaa_timeseries_solar_position
from pvgisprototype.web_api.geometry.noaa.irradiance import get_calculate_effective_irradiance_time_series

from pvgisprototype.plot.plot_solar_declination import plot_solar_declination_one_year_bokeh
from pvgisprototype.web_api.plot.plot_example import plot_example
from pvgisprototype.web_api.plot.plot_example import graph_example
from pvgisprototype.constants import RADIANS

from pathlib import Path
current_file = Path(__file__).resolve()
assets_directory = current_file.parent / "web_api/assets"


app = FastAPI()
# app.mount("/static", StaticFiles(directory="pvgisprototype/web_api/assets"), name="static")
app.mount("/static", StaticFiles(directory=str(assets_directory)), name="static")
templates = Jinja2Templates(directory="templates")


from jinja2 import Template
template = Template('''<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title>LV Sensors</title>
        {{ js_resources }}
        {{ css_resources }}
    </head>
    <body>
    {{ plot_div }}
    {{ plot_script }}
    </body>
</html>
''')


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>PVGIS</title>
            <style>
                body {
                    text-align: center; /* Centering text for the whole body */
                    font-family: Arial, sans-serif; /* Optional: setting a nice default font */
                }
                .title {
                    color: #003399;  /* European Commission Blue */
                    font-size: 60px; /* Larger Size */
                    font-weight: bold; /* Bold Font */
                    background-color: yellow; /* Yellow Background */
                    display: inline-block;
                    padding: 10px;
                    margin-top: 20px; /* Space at the top */
                }
                .subtitle {
                    font-size: 24px; /* Larger Font Size for Subtitle */
                    margin-top: 10px; /* Space between title and subtitle */
                }
                .logo {
                    display: block;
                    margin: 20px auto; /* Center the logo and add space around it */
                }
                ul.links {
                    list-style-type: disc;
                    padding-left: 0; /* Align with centered text */
                    display: inline-block; /* Aligns the list with center */
                    text-align: left; /* Aligns text to the left inside the list */
                }
                ul.links li {
                    margin-bottom: 10px;
                }
                ul.links a {
                    color: #8A2BE2;
                    text-decoration: none;
                    font-size: 18px;
                }
                ul.links a:hover {
                    text-decoration: underline;
                    color: #BA55D3;
                }
            </style>
        </head>
        <body>
            <div class="title">PVGIS</div>
            <div class="subtitle">Welcome to PVGIS' API</div>

            <ul class="links">
                <li><a href="/docs">API Documentation</a></li>
                <li><a href="http://pvgis-manual.jrc.it">PVGIS manual</a> The on-line manual is freely accessible from inside the JRC network.</li>
                <li><a href="http://gitlab.com/ec-jrc-c2/pvgis/pvgis-manual">The manual also lives at gitlab.io</a> Access to gitlab.io is granted to members of the private repository.</li>
            </ul>

            <!-- Local image from static files -->
            <img class="logo" src="/static/eu_logo.png" alt="European Commission Logo"/>
        </body>
    </html>
    """


class SolarTimeResult(BaseModel):
    Model: str
    Solar_time: float
    Units: str


app.get("/calculate/geometry/solar_time/")(get_calculate_solar_time)
app.get("/calculate/geometry/overview")(get_calculate_solar_geometry_overview)
app.get("/calculate/geometry/overview_series")(get_calculate_noaa_timeseries_solar_position)

app.get("/calculate/irradiance/effective")(get_calculate_effective_irradiance_time_series)

app.get("/plot/example", response_class=HTMLResponse)(plot_example)
app.get("/plot/graph", response_class=HTMLResponse)(graph_example)


@app.get("/plot/solar_declination_one_year_bokeh", response_class=HTMLResponse)
async def get_plot(
        request: Request,
        year: int,
        title: Optional[str] = 'Annual Variation of Solar Declination',
        output_units: Optional[str] = RADIANS,
        inline: Optional[bool] = True
        ):
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = plot_solar_declination_one_year_bokeh(
            year,
            title,
            output_units
            )

    return templates.TemplateResponse(
            "plot.html",
            {
                "request": request,
                "plot_script": script,
                "plot_div": div,
                "js_resources":js_resources,
                "css_resources":css_resources,
                }
            )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
