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


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=':chart_increasing:  Retrieve time series of meteorological variables',
)


def read_raster_data(netcdf: str, mask_and_scale=False):
    """
    """
    pass
