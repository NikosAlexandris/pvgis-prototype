from devtools import debug

from typing import Annotated
from typing import Union
from typing import Optional
from typing import List
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi import Query
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from datetime import datetime

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.resources import CDN

# from pvgisprototype.api.utilities.conversions import convert_to_radians_fastapi
# from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
# from pvgisprototype.api.utilities.timestamp import convert_to_timezone

from pvgisprototype.web_api.geometry.noaa.solar_position import get_calculate_solar_geometry_overview
from pvgisprototype.web_api.geometry.solar_time import get_calculate_solar_time
from pvgisprototype.web_api.geometry.noaa.solar_position import get_calculate_noaa_timeseries_solar_position
from pvgisprototype.web_api.geometry.noaa.irradiance import get_calculate_effective_irradiance_time_series

# from pvgisprototype.plot.plot import plot_line
from pvgisprototype.plot.plot_solar_declination import plot_solar_declination_one_year_bokeh
from pvgisprototype.web_api.plot.plot_example import plot_example
from pvgisprototype.web_api.plot.plot_example import graph_example
from pvgisprototype.constants import RADIANS


app = FastAPI()
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


@app.get("/")
def read_root():
    return {"Hello": "World"}


class SolarTimeResult(BaseModel):
    Model: str
    Solar_time: float
    Units: str


app.get("/calculate/geometry/solar_time/")(get_calculate_solar_time)

app.get("/calculate/geometry/overview")(get_calculate_solar_geometry_overview)


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
