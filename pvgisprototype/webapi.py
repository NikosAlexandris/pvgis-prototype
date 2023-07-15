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


from .api.geometry.time.models import SolarTimeModels
from .api.geometry.solar_time import calculate_solar_time

from .api.utilities.conversions import convert_to_radians_fastapi
from .api.utilities.timestamp import now_utc_datetimezone
from .api.utilities.timestamp import convert_to_timezone

from .plot.plot import plot_line
from .plot.plot_solar_declination import plot_solar_declination_one_year_bokeh

from .web_api.geometry.noaa.solar_position import noaa_solar_position



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


# @app.get("/calculate_solar_time/", response_model=List[SolarTimeResult])
@app.get("/calculate_solar_time/")
async def get_solar_time(
    longitude: float = Query(..., ge=-180, le=180),
    latitude: float = Query(..., ge=-90, le=90),
    timestamp: Optional[datetime] = None,
    timezone: Optional[str] = None,
    model: List[SolarTimeModels] = Query([SolarTimeModels.skyfield], description="Model to calculate solar time"),
    days_in_a_year: float = Query(365.25, description="Days in a year"),
    perigee_offset: float = Query(0.048869, description="Perigee offset"),
    eccentricity: float = Query(0.01672, description="Eccentricity"),
    time_offset_global: float = Query(0, description="Global time offset"),
    hour_offset: float = Query(0, description="Hour offset"),
):
    debug(locals())
    longitude = convert_to_radians_fastapi(longitude)
    latitude = convert_to_radians_fastapi(latitude)

    if timestamp is None:
        timestamp = now_utc_datetimezone()

    if timezone:
        timezone = convert_to_timezone(timezone)
        timestamp = timestamp.astimezone(timezone)
    
    debug(locals())
    solar_time  = calculate_solar_time(
            longitude,
            latitude,
            timestamp,
            timezone,
            model,
            days_in_a_year,
            perigee_offset,
            eccentricity,
            time_offset_global,
            hour_offset,
            )
    debug(locals())
    return {"Local solar time": solar_time}


app.get("/calculate/geometry/noaa/solar_position")(noaa_solar_position)


@app.get("/plot", response_class=HTMLResponse)
async def get_plot(
        request: Request,
        inline: bool=True
        ):
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = plot_line()

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


@app.get("/plot_solar_declination_one_year_bokeh", response_class=HTMLResponse)
async def get_plot(
        request: Request,
        year: int,
        title: Optional[str] = 'Annual Variation of Solar Declination',
        output_units: Optional[str] = 'radians',
        inline: Optional[bool] = True
        ):
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = plot_solar_declination_one_year_bokeh(year, title)

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


@app.get("/graph", response_class=HTMLResponse)
async def read_root(request: Request, inline: bool=True):
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    p = figure(title="Title for the plot", x_axis_type='datetime', y_axis_type="linear")

    script, div = components(p, INLINE)
    # script, div = plot_line()

    if inline:
        return template.render(
                plot_script=script,
                plot_div=div,
                js_resources=js_resources,
                css_resources=css_resources,
                )
    else:
        return templates.TemplateResponse(
                "graph.html",
                {
                    "request":request,
                    "plot_script":script,
                    "plot_div":div,
                    "js_resources":js_resources,
                    "css_resources":css_resources,
                    }
                )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="localhost",port=8001)
