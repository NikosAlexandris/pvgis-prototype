import typer
from rich import print
from typing_extensions import Annotated

from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.typer.efficiency import typer_argument_conversion_efficiency
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.typer.location import (
    typer_argument_latitude,
    typer_argument_longitude,
)
from pvgisprototype.cli.typer.photovoltaic import typer_argument_area
from pvgisprototype.utilities.cf_conventions import comply_dataset_to_cf_conventions
from pvgisprototype.utilities.merge_datasets import merge_datasets


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=":toolbox:  Diagnostic functions",
)


app.command(
    name="comply-dataset-to-cf-conventions",
    help=f"Transform primitive SARAHx NetCDF data files to a spatiotemporal Dataset compliant to CF conventions [bold yellow]Prototype[/bold yellow]",
    no_args_is_help=False,
)(comply_dataset_to_cf_conventions)
app.command(
    name="merge-datasets",
    help=f"Merge CF conventions compliant SARAHx NetCDF data files to a single spatiotemporal Dataset [bold yellow]Prototype[/bold yellow]",
    no_args_is_help=False,
)(merge_datasets)


@app.command(
    "get-horizon",
    no_args_is_help=True,
    help=f"⦩⦬ Calculate the horizon angle height around a single point based on a digital elevation model {NOT_IMPLEMENTED_CLI}",
)
def get_horizon(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
):
    """Calculate the entire horizon angle height (in radians) around a single point from a digital elevation model

    Notes:
        - Based on the original C program `horizon_out`
        - Variable, Typr, Range, Default, Notes
        - lat, float, [-90, 90], -, Latitude in decimal degrees, south is negative. Required
        - lon, float, [-180, 180], - , Longitude in decimal degrees, west is negative. Required
        - userhorizon, list, List of float values ranging in [0, 90] separated by comma (CSV) (length < =365), -, Height of the horizon at equidistant directions around the point of interest, in degrees.
          Starting at north and moving clockwise. The series 0, 10, 20, 30, 40,
          15, 25, 5 would mean the horizon height is 0° due north, 10° for
          north-east, 20° for east, 30° for south-east, and so on. Optional,
          Depends on `userhorizon=1`,
        - outputformat, str, [csv, basic, json], csv, Output format. csv: CSV with text explanations, basic: CSV. Optional
        - browser, bool, 0, 1, 0, Setting browser=1 and accessing the service through a web browser, will save the retrieved data to a file. Optional
    """
    pass


@app.command(
    "get-elevation",
    no_args_is_help=True,
    help=f"Retrieve the location elevation from digital elevation data {NOT_IMPLEMENTED_CLI}",
)
def get_elevation(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
):
    """
    Retrieve the location elevation from digital elevation data

    Args:
        longitude
        latitude

    Notes:
        - Based on the original C program `readelevation`:
        - Variable, Type, Range, Default, Notes
        - lat, float, [-90, 90], -, Required
        - lon, float, [-180, 180], -, Required
    """
    pass


@app.command(
    "list-databases",
    no_args_is_help=True,
    help=f"List solar irradiance databases {NOT_IMPLEMENTED_CLI}",
)
def list_databases(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
):
    """
    List available databases for a location

    Args:
        longitude
        latitude
        databases: List of the default databases in PVGIS: PVGIS-SARAH2, PVGIS-SARAH, PVGIS-ERA5, PVGIS-CMSAF, PVGIS-COSMO, PVGIS-NSRDB
    Notes:
        - Based on the original C program `gisbinextract` and a file called `tilecoverage_dbname`
        - Variable, Type, M/O, Range, Default, Dependencies
        -lat, float, M, [-90, 90], -, -
        -lon, float, M, [-180, 180], -, -,
        -raddatabase, str, [[PVGIS-SARAH2](database:datasets:solar-radiation-data:sarah2), <br>[PVGIS-SARAH](database:datasets:solar-radiation-data:sarah), <br>[PVGIS-ERA5](database:datasets:solar-radiation-data:era5), <br>[PVGIS-CMSAF](database:datasets:solar-radiation-data:cmsaf), <br>[PVGIS-COSMO](database:datasets:solar-radiation-data:cosmo), <br>[PVGIS-NSRDB](database:datasets:solar-radiation-data:nsrdb)], Defaultdatabase, Optional
    """
    databases = [
        "PVGIS-SARAH2",
        "PVGIS-SARAH",
        "PVGIS-ERA5",
        "PVGIS-CMSAF",
        "PVGIS-COSMO",
        "PVGIS-NSRDB",
    ]
    if longitude is None and latitude is None:
        print(f"PVGIS databases:\n{databases}")
    else:
        try:
            location = (longitude, latitude)
            typer.secho(
                f"The available databases for the requested location {location} are:\n {databases}",
                fg=typer.colors.MAGENTA,
            )
            return 0
        except Exception as exc:
            typer.echo(f"Something went wrong: {str(exc)}")
            raise typer.Exit(code=33)


@app.command(
    "peak-power",
    no_args_is_help=True,
    help=f"Calculate the peak power in kW based on area and conversion efficiency {NOT_IMPLEMENTED_CLI}",
)
def calculate_peak_power(
    area: Annotated[float, typer_argument_area],
    conversion_efficiency: Annotated[float, typer_argument_conversion_efficiency],
):
    """Calculate the peak power in kW based on area and conversion efficiency

    .. math:: Power = 1/m^{2} * area * efficiency / 100

    Returns:
        Power in kWp
    """
    power = 1 / area * conversion_efficiency / 100
    return power
