import typer
import xarray as xr
from .rich_help_panel_names import rich_help_panel_series_irradiance
from .rich_help_panel_names import rich_help_panel_series_meteorology

from . import irradiance
from . import tmy
from . import meteorology


# series:
#   irradiance:
#     - global
#     - direct
#     - diffuse
#     - infrared
#     - data-bases
#   meteorology:
#     - temperature
#     - wind-speed
#     - wind-direction
#     - humidity
#     - air-pressure
#     - tmy

app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=':chart_increasing:  Retrieve time series of solar radiation and PV power output',
)


@app.command()
def query_location(
        netcdf: str,
        longitude: float,
        latitude: float,
        mask_and_scale=False,
        method='nearest',
        ) -> int:
    """
    Query the value or time series over a specific location - Example command!
    """
    try:
        dataarray = read_raster_data(netcdf, mask_and_scale=mask_and_scale)
        data = dataarray.sel(
                lon=longitude,
                lat=latitude,
                method='nearest',
                )
        output = data.values.tolist()
        typer.echo(output)
        return 0

    except Exception as exc:
        typer.echo(f"Error: {str(exc)}")
        return 1
