import typer
from typing_extensions import Annotated
from typing import Optional
from rich import print


app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    help=f"PVGIS core CLI prototype",
)


@app.command()
def get_horizon(
        longitude: Annotated[Optional[float], typer.Argument(default=None, min=-180, max=180)],
        latitude: Annotated[Optional[float], typer.Argument(default=None, min=-90, max=90)],
        ):
    """Computes the entire horizon angle height (in radians) around a single point from a digital elevation model

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


@app.command()
def get_elevation(
        longitude: Annotated[float, typer.Argument(..., min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(..., min=-90, max=90)],
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


@app.command()
def list_databases(
        longitude: Annotated[float, typer.Argument(default=None, min=-180, max=180)] = None,
        latitude: Annotated[float, typer.Argument(default=None, min=-90, max=90)] = None,
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
    databases = ['PVGIS-SARAH2', 'PVGIS-SARAH', 'PVGIS-ERA5', 'PVGIS-CMSAF', 'PVGIS-COSMO', 'PVGIS-NSRDB']
    if longitude is None and latitude is None:
        print(f'PVGIS databases:\n{databases}')
    else:
        try: 
            location = (longitude, latitude)
            typer.secho(f"The available databases for the requested location {location} are:\n {databases}", fg=typer.colors.MAGENTA)
            return 0
        except Exception as exc:
            typer.echo(f"Something went wrong: {str(exc)}")
            raise typer.Exit(code=33)
