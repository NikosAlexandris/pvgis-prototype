import typer
from typing_extensions import Annotated
from typing import Optional
from click import Context
from typer.core import TyperGroup

from .rich_help_panel_names import rich_help_panel_series_irradiance
from .rich_help_panel_names import rich_help_panel_toolbox
from ..api.irradiance.extraterrestrial import app as extraterrestrial_irradiance
from ..api.irradiance.shortwave import app as global_irradiance
from ..api.irradiance.direct import app as direct_irradiance
from ..api.irradiance.diffuse import app as diffuse_irradiance
from ..api.irradiance.reflected import app as reflected_irradiance
from ..api.irradiance.loss import app as angular_loss_factor
from ..api.irradiance.effective import app as effective_irradiance


class OrderCommands(TyperGroup):
  def list_commands(self, ctx: Context):
    """Return list of commands in the order appear.
    See: https://github.com/tiangolo/typer/issues/428#issuecomment-1238866548
    """
    return list(self.commands)    # get commands using self.commands


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":sun_with_face: Calculate solar irradiance",
)


app.add_typer(
    effective_irradiance,
    name="effective",
    help="Estimate the effective irradiance for a specific hour",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    global_irradiance,
    name="global",
    help="Estimate or read global (shortwave) irradiance time series",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    direct_irradiance,
    name="direct",
    help="Estimate the direct irradiance incident on a horizontal or inclined surface",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    diffuse_irradiance,
    name="diffuse",
    help="Estimate the diffuse irradiance",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    reflected_irradiance,
    name="reflected",
    help=f'Calculate the clear-sky ground reflected irradiance',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    extraterrestrial_irradiance,
    name="extraterrestrial",
    help="Estimate the solar constant for a day of the year",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    angular_loss_factor,
    name="angular-loss",
    help="Estimate the angular loss factor for the direct horizontal irradiance",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
