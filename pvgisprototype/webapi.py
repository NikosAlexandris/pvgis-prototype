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

from pvgisprototype.web_api.series.select import select
from pvgisprototype.web_api.geometry.overview import get_calculate_solar_geometry_overview
from pvgisprototype.web_api.geometry.solar_time import get_calculate_solar_time
from pvgisprototype.web_api.geometry.overview_series import overview_series
from pvgisprototype.web_api.irradiance.energy import get_photovoltaic_power_output_series

from pvgisprototype.plot.plot_solar_declination import plot_solar_declination_one_year_bokeh
from pvgisprototype.web_api.plot.plot_example import plot_example
from pvgisprototype.web_api.plot.plot_example import graph_example
from pvgisprototype.constants import RADIANS
from pathlib import Path


current_file = Path(__file__).resolve()
assets_directory = current_file.parent / "web_api/assets"

description = """
PVGISAPI is a public service supported by the European Commission. 🇪🇺

### Photovoltaic Potential 

Various technologies

- Grid-connected 🔌
- Stand-alone 🔋
- Models available in [PVMAPS](https://ec.europa.eu/jrc/en/PVGIS/downloads/PVMAPS) 

### Hourly series of

- Solar radiation
- PV performance 📈
- Temperature 🌡️
- Typical Meteorological Year for 9 climate variables

### Print Ready

Country/regional maps of

- Solar resource
- Photovoltaic potential 🗺️

### Coverage

- Europe & Africa 🌍
- Largely Asia 🌏
- America 🌎

### Languages

/media/svg/languages-in-pvgis.svg

### Public Service

/media/svg/european-flag-edit.svg

- Cost free
- Open access ✨
"""

app = FastAPI(
    title="PVGISAPI",
    description=description,
    summary="PVGIS public API",
    version="0.0.1",
    terms_of_service="https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/pvgis-background-information/data-protection_en",
    contact={
        "name": "PVGIS, Joint Research Centre, European Commission",
        "url": "https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/pvgis-background-information/pvgis-contact-points_en",
        "email": "JRC-PVGIS@ec.europa.eu",
    },
    # license_info={
    #     "name": "",
    #     "url": "",
    # },
)

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
                    text-align: center;
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: #f4f4f4; /* Light grey background */
                }
                .header {
                    background-color: #003399; /* EC Blue */
                    color: white;
                    padding: 10px 0;
                }
                .title {
                    font-size: 70px; /* Increased Size */
                    margin-bottom: 10px; /* Space after title */
                }
                .subtitle {
                    font-size: 30px; /* Increased Size */
                    margin-bottom: 20px; /* Space after subtitle */
                }
                .poc-banner {
                    background-color: #ffcc00; /* EC Yellow */
                    color: black;
                    padding: 5px 0;
                    font-size: 20px;
                    font-weight: bold;
                }
                .content {
                    padding: 20px;
                }
                ul.links {
                    list-style-type: none;
                    padding: 0;
                }
                ul.links li {
                    margin-bottom: 10px;
                }
                ul.links a {
                    color: #003399; /* EC Blue */
                    text-decoration: none;
                    font-size: 18px;
                    margin-right: 30px;
                }
                ul.links a:hover {
                    text-decoration: underline;
                }
                .explanation {
                    font-size: 14px; /* Smaller than main text */
                    color: #555; /* Subtle color */
                    font-style: italic; /* Italicize the text */
                    margin-left: 20px; /* Indent for distinction */
                    line-height: 1.6; /* Adjust line spacing */
                }
                .footer {
                    display: flex;
                    align-items: center; /* Align items vertically */
                    justify-content: center; /* Center items horizontally */
                    /* Other styling as required */
                }
                .footer-logo {
                    width: 100px; /* Adjust as needed */
                    height: auto; /* Maintain aspect ratio */
                    margin-right: 20px; /* Space between logo and text */
                }
                .footer-text {
                    text-align: left;
                    /* Additional styling for the text */
                }
                .footer {
                    background-color: #f4f4f4; /* Light grey background */
                    color: #333; /* Dark text for readability */
                    font-size: 14px;
                    text-align: center;
                    padding: 20px;
                    margin-top: 30px; /* Space above the footer */
                    border-top: 1px solid #ddd; /* A subtle top border */
                }
                .footer a {
                    color: #003399; /* EC Blue */
                    text-decoration: none;
                }
                .footer a:hover {
                    text-decoration: underline;
                }
                #globeViz {
                    width: 250px;
                    height: 250px;
                    margin: auto;
                    overflow: hidden;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    position: relative;
                }
            </style>

            <script src="//unpkg.com/three"></script>
            <script src="//unpkg.com/globe.gl"></script>

        </head>
        <body>
            <div class="header">
                <div class="title">PVGIS</div>
                <div class="subtitle">Welcome to PVGIS' interactive resources</div>
            </div>
            <div class="poc-banner">Work in Progress</div>
            <div class="content">
                <ul class="links">
                    <li><a href="/docs">API</a>  <a href="http://pvgis-manual.jrc.it">Manual</a>  <a href="http://pvgis-forum.jrc.it">Forum</a></li>
                    <div class="explanation">Resources currently accessible only from inside the JRC network</div>
                </ul>
            </div>

            <div id="globeViz"></div>

            <script>
              // Initialize the globe variable outside the fetch block to ensure it's accessible throughout the script
              let world;

              fetch('/static/sample.geojson').then(res => res.json()).then(data => {
                // Define the globe inside the fetch's success callback
                world = Globe()
                  .width(300)
                  .height(300)
                  .backgroundColor('#f4f4f4')
                  .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
                  .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
                  .pointOfView({ altitude: 100 })
                  .labelsData(data.features)
                  .labelLat(d => d.geometry.coordinates[1])
                  .labelLng(d => d.geometry.coordinates[0])
                  .labelText(d => d.properties.country_name)
                  .labelColor(() => 'rgba(255, 165, 0, 0.75)')
                  .labelResolution(2)
                  (document.getElementById('globeViz'));

                // Custom globe material setup
                setupGlobeMaterial(world);
              });

              // Function to set up custom globe material
              function setupGlobeMaterial(globe) {
                const globeMaterial = globe.globeMaterial();
                globeMaterial.bumpScale = 10;

                new THREE.TextureLoader().load('https://unpkg.com/three-globe/example/img/earth-water.png', texture => {
                  globeMaterial.specularMap = texture;
                  globeMaterial.specular = new THREE.Color('grey');
                  globeMaterial.shininess = 15;
                });

                // Auto-rotate
                globe.controls().autoRotate = true;
                globe.controls().autoRotateSpeed = 0.35;

                const directionalLight = globe.lights().find(light => light.type === 'DirectionalLight');
                directionalLight && directionalLight.position.set(1, 1, 1);
              }
            </script>

            <div class="footer">
                <img class="footer-logo" src="/static/eu_logo.png" alt="European Commission Logo"/>
                <div class="footer-text">
                    Last updated on Nov 01, 2023 by the PVGIS Team<br>
                    This work is licensed under a <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">Creative Commons Attribution 4.0 International License</a>.<br>
                    All content © European Union/European Atomic Energy Community 2021 | <a href="https://ec.europa.eu/jrc/en" target="_blank">EU Science Hub</a>
                </div>
            </div>

        </body>
    </html>
    """


class SolarTimeResult(BaseModel):
    Model: str
    Solar_time: float
    Units: str


# series
app.get("/calculate/series/select")(select)

# geometry
app.get("/calculate/geometry/solar_time/")(get_calculate_solar_time)
app.get("/calculate/geometry/overview")(get_calculate_solar_geometry_overview)
app.get("/calculate/geometry/overview_series")(overview_series)

# irradiance
app.get("/calculate/irradiance/effective")(get_photovoltaic_power_output_series)

# plot
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
