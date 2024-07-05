from pathlib import Path
from typing import Tuple

import typer
from typing_extensions import Annotated

app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=":thermometer:  Generate a Typical Meteorological Year",
)


def calculate_degree_days(
    location: Annotated[
        Tuple[float, float], typer.Argument(..., help="Latitude, longitude [°]")
    ],
    years: Annotated[
        Tuple[float, float],
        typer.Argument(
            ..., min=2005, max=2020, help="First and last year of calculations"
        ),
    ],
    meteo: Annotated[
        Path,
        typer.Argument(
            ...,
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="Directory containing the meteorological data",
        ),
    ],
    elevation: Annotated[
        Path,
        typer.Argument(
            ...,
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="Directory containing the digital elevation data",
        ),
    ],
    monthly: bool = typer.Option(False, is_flag=True, help="Print monthly averages"),
):
    """Calculate the cooling/heating degree days

    Args:

    Returns:
        None

    Raises:
        AssertionError: If the command exit code or output doesn't match the expected values.

    Example:

    Notes:
    - Refactored from the original C program `degreedays_hourly` as follows:\n
      - New flag, Old flag, Type, Old Variable, Description\n
      - monthly   , r    , Flag         , -                   , Print monthly averages \n
      - meteo     , g    , str          , dailyPrefix         , Directory containing the meteo files\n
      - elevation , f    , str          , elevationFilename   , Directory prefix of the DEM files\n
      - location  , d    , float, float , latitude, longitude , Latitude, longitude [°]\n
      - years     , y    , float, float , yearStart, yearEnd  , First year, last year of calculations
    """
    pass


@app.command("tmy")
def generate_tmy():
    """Generate the Typical Meteorological Year

    A typical meteorological year (TMY) is a set of meteorological data with
    data values for every hour in a year for a given geographical location. The
    data are selected from hourly data in a longer time period (normally 10
    years or more). The TMY tool can be used to interactively visualise all the
    data or to download the data as a text file.
    """
    pass


if __name__ == "__main__":
    app()
