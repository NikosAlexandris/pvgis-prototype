import typer

from pvgisprototype.cli.irradiance.direct.horizontal import (
    get_direct_horizontal_irradiance_series,
)
from pvgisprototype.cli.irradiance.direct.inclined import (
    get_direct_inclined_irradiance_series,
)
from pvgisprototype.cli.irradiance.direct.normal import (
    get_direct_normal_irradiance_series,
)
from pvgisprototype.cli.irradiance.direct.normal_from_horizontal import (
    get_direct_normal_from_horizontal_irradiance_series,
)
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_irradiance_series
from pvgisprototype.cli.typer.group import OrderCommands

app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=":sun_with_face: Estimate the direct solar irradiance incident on a solar surface",
)
app.command(
    name="normal",
    help="Estimate the direct normal irradiance over a period of time",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_direct_normal_irradiance_series)
app.command(
    name="normal-from-horizontal",
    help="Estimate the direct normal from the horizontal irradiance over a period of time",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_direct_normal_from_horizontal_irradiance_series)
app.command(
    name="horizontal",
    help="Estimate the direct horizontal irradiance over a period of time",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_direct_horizontal_irradiance_series)
app.command(
    "inclined",
    help="Estimate the direct inclined irradiance over a period of time",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_direct_inclined_irradiance_series)
