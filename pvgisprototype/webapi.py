from typing import Union
from typing import Optional

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

from .solar_time import calculate_solar_time_skyfield
from .timestamp import now_datetime
from .timestamp import convert_to_timezone
from .plot import plot_line
from .solar_declination_plot import plot_solar_declination_one_year_bokeh


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


@app.get("/calculate_solar_time_skyfield/")
async def get_solar_time_skyfield(
    longitude: float = Query(..., ge=-180, le=180),
    latitude: float = Query(..., ge=-90, le=90),
    timestamp: datetime = Query(default_factory=now_datetime),
    timezone: Optional[str] = None,
):
    timezone = convert_to_timezone(timezone)
    decimal_hours = calculate_solar_time_skyfield(longitude, latitude, timestamp, timezone)
    return {"Local solar time": decimal_hours}


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
