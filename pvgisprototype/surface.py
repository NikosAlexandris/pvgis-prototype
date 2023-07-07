from devtools import debug
import typer
from typing import Annotated
from typing import Optional
from typing import Union
from typing import List
from rich.console import Console


console = Console()
app = typer.Typer(
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":triangular_ruler:  Calculate solar surface geometry parameters for a location and moment in time",
)


@app.command('surface', no_args_is_help=True, help='Calculate solar surface geometry parameters (tilt, orientation)')
def surface(
        output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Output units for solar geometry variables (degrees or radians)")] = 'radians',
        rounding_places: Annotated[Optional[int], typer.Option(
            '-r',
            '--rounding-places',
            show_default=True,
            help='Number of places to round results to.')] = 5,
        ):
    """
    """
    print('Not implemented')
