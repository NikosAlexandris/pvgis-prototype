import typer
from typing_extensions import Annotated
from typing import Optional
from click import Context
from typer.core import TyperGroup

from .rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_efficiency
from .rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.api.irradiance.extraterrestrial import app as extraterrestrial_irradiance
from pvgisprototype.api.irradiance.extraterrestrial_time_series import app as extraterrestrial_irradiance_series
from pvgisprototype.api.irradiance.direct import app as direct_irradiance
from pvgisprototype.api.irradiance.direct_time_series import app as direct_irradiance_series
from pvgisprototype.api.irradiance.diffuse import app as diffuse_irradiance
from pvgisprototype.api.irradiance.diffuse_time_series import app as diffuse_irradiance_series
from pvgisprototype.api.irradiance.reflected import app as reflected_irradiance
from pvgisprototype.api.irradiance.reflected_time_series import app as reflected_irradiance_series
from pvgisprototype.api.irradiance.shortwave import app as global_irradiance  # global is a Python reserved keyword!
from pvgisprototype.api.irradiance.global_time_series import app as global_irradiance_series
from pvgisprototype.api.irradiance.loss import app as angular_loss_factor
from pvgisprototype.api.irradiance.effective import app as effective_irradiance
from pvgisprototype.api.irradiance.effective_time_series import app as effective_irradiance_series
from pvgisprototype.api.irradiance.efficiency import app as pv_efficiency
from pvgisprototype.api.irradiance.efficiency_time_series import app as pv_efficiency_series
from pvgisprototype.api.irradiance.limits import app as limits

from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.messages import TO_MERGE_WITH_SINGLE_VALUE_COMMAND


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    # help=f":sun_with_face: Estimate the solar irradiance incident on a horizontal or inclined surface",
    help=f":sun_with_face: Estimate the solar irradiance incident on a solar surface",
)
app.add_typer(
    effective_irradiance,
    name="effective",
    help="Estimate the effective irradiance for a specific hour",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    effective_irradiance_series,
    name="effective-series",
    help="Estimate the effective irradiance over a time series",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    global_irradiance,
    name="global",
    help="Estimate the global irradiance for a specific hour",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    global_irradiance_series,
    name="global-series",
    help="Estimate the global irradiance over a time series",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    direct_irradiance,
    name="direct",
    help="Estimate the direct irradiance",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    direct_irradiance_series,
    name="direct-series",
    help=f'Estimate the direct irradiance over a period of time {TO_MERGE_WITH_SINGLE_VALUE_COMMAND}',
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
    diffuse_irradiance_series,
    name="diffuse-series",
    help=f'Estimate the diffuse irradiance over a period of time {TO_MERGE_WITH_SINGLE_VALUE_COMMAND}',
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
    reflected_irradiance_series,
    name="reflected-series",
    help=f'Calculate the clear-sky ground reflected irradiance over a period of time {TO_MERGE_WITH_SINGLE_VALUE_COMMAND}',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    extraterrestrial_irradiance,
    name="extraterrestrial",
    help="Calculate the extraterrestial irradiance for a day of the year",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    extraterrestrial_irradiance_series,
    name="extraterrestrial-series",
    help="Calculate the extraterrestial irradiance for a time series",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    angular_loss_factor,
    name="angular-loss",
    help=f"Estimate the angular loss factor for the direct horizontal irradiance {NOT_IMPLEMENTED_CLI}",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    pv_efficiency,
    name="pv-efficiency",
    no_args_is_help=True,
    # rich_help_panel=rich_help_panel_efficiency,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    pv_efficiency_series,
    name="pv-efficiency-series",
    no_args_is_help=True,
    # rich_help_panel=rich_help_panel_efficiency,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    limits,
    name="limits",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
