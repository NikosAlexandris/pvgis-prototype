from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from click import Context
from datetime import datetime
from devtools import debug
from enum import Enum
from math import cos
from pathlib import Path
from pvgisprototype.api.geometry.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SolarIncidenceModels
from pvgisprototype.api.geometry.models import SolarDeclinationModels
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.geometry.altitude_series import model_solar_altitude_time_series
from pvgisprototype.api.geometry.incidence_series import model_solar_incidence_time_series
from pvgisprototype.api.geometry.solar_time_series import model_solar_time_time_series
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
# from pvgisprototype.cli.irradiance.effective import app as effective_irradiance
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT
from pvgisprototype.cli.irradiance.efficiency import app as pv_efficiency
from pvgisprototype.api.irradiance.limits import app as limits
from pvgisprototype.cli.irradiance.shortwave import app as global_irradiance
from pvgisprototype.cli.irradiance.direct import app as direct_irradiance
from pvgisprototype.cli.irradiance.diffuse import app as diffuse_irradiance
from pvgisprototype.cli.irradiance.reflected import app as reflected_irradiance
from pvgisprototype.cli.irradiance.extraterrestrial import app as extraterrestrial_irradiance
from pvgisprototype.api.irradiance.loss import app as angular_loss_factor
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_to_radians
from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours_time_series
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.messages import TO_MERGE_WITH_SINGLE_VALUE_COMMAND
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_atmospheric_properties
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_earth_orbit
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_efficiency
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_geometry_surface
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_time
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.documentation import A_PRIMER_ON_SOLAR_IRRADIANCE
from pvgisprototype.validation.functions import ModelSolarPositionInputModel
from rich import print
import math
import numpy as np
import typer


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    # help=f":sun_with_face: Estimate the solar irradiance incident on a horizontal or inclined surface",
    help=f":sun_with_face: Estimate the solar irradiance incident on a solar surface",
)


@app.command(
    'intro',
    no_args_is_help=False,
    help='A short primer on solar irradiance',
 )
def intro():
    """A short introduction on solar geometry"""
    introduction = """
    [underline]Solar irradiance[/underline] is ...
    """
    note = """
    PVGIS can model solar irradiance components or read selectively
    [magenta]global[/magenta] or [magenta]direct[/magenta] irradiance time series from external datasets.
    """
    from rich.panel import Panel
    note_in_a_panel = Panel(
        "[italic]{}[/italic]".format(note),
        title="[bold cyan]Note[/bold cyan]",
        width=78,
    )
    from rich.console import Console
    console = Console()
    # introduction.wrap(console, 30)
    console.print(introduction)
    console.print(note_in_a_panel)
    console.print(A_PRIMER_ON_SOLAR_IRRADIANCE)
# app.add_typer(
#     effective_irradiance,
#     name="effective",
#     help="Estimate the effective irradiance over a time series",
#     no_args_is_help=True,
#     rich_help_panel=rich_help_panel_series_irradiance,
# )
app.add_typer(
    pv_efficiency,
    name="pv-efficiency",
    no_args_is_help=True,
    # rich_help_panel=rich_help_panel_efficiency,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    global_irradiance,
    name="global",
    help=f"Estimate the global irradiance over a time series",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    direct_irradiance,
    name="direct",
    help=f'Estimate the direct irradiance over a period of time',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    diffuse_irradiance,
    name="diffuse",
    help=f'Estimate the diffuse irradiance over a period of time',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    reflected_irradiance,
    name="reflected",
    help=f'Calculate the clear-sky ground reflected irradiance over a period of time',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    extraterrestrial_irradiance,
    name="extraterrestrial",
    help=f"Calculate the extraterrestial irradiance for a time series",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    angular_loss_factor,
    name="angular-loss",
    help=f"Estimate the angular loss factor for the direct horizontal irradiance {NOT_IMPLEMENTED_CLI}",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    limits,
    name="limits",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
