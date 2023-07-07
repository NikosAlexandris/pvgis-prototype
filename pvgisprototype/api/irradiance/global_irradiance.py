"""
Global irradiance
"""

import logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('error.log'),  # Save log to a file
        logging.StreamHandler()  # Print log to the console
    ]
)
import typer
from typing import Annotated
from typing import Optional
from typing import Union
from datetime import datetime


console = Console()
app = typer.Typer(
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Estimate the global solar irradiation",
)


def calculate_global_irradiance(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_datetime)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
    ):
    """Calculate the global irradiatiance incident on a solar surface.

    Parameters
    ----------

    Returns
    -------
    global_irradiance: float
        The global radiant flux incident on a surface per unit area in W/m².
    """
    pass
