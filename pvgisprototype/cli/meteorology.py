"""
meteorology:

  - temperature
  - wind-speed
  - wind-direction
  - humidity
  - air-pressure
  - tmy
"""
import typer
from .messages import NOT_IMPLEMENTED


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=':sun_behind_rain_cloud:  Meteorological time series',
)


@app.callback(
        help='')
def read_raster_data(netcdf: str, mask_and_scale=False):
    """
    """
    print(f"{NOT_IMPLEMENTED}")
