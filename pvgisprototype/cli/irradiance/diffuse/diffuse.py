import typer

from pvgisprototype.cli.irradiance.diffuse.altitude import (
    get_diffuse_solar_altitude_coefficients_series,
    get_diffuse_solar_altitude_function_series,
)
from pvgisprototype.cli.irradiance.diffuse.horizontal import (
    get_diffuse_horizontal_irradiance_series,
)
from pvgisprototype.cli.irradiance.diffuse.horizontal_from_sarah import (
    get_diffuse_horizontal_from_global_and_direct_irradiance,
)
from pvgisprototype.cli.irradiance.diffuse.inclined import (
    get_diffuse_inclined_irradiance_series,
)
from pvgisprototype.cli.irradiance.diffuse.sky_irradiance import (
    get_diffuse_sky_irradiance_series,
)
from pvgisprototype.cli.irradiance.diffuse.term_n import get_term_n_series
from pvgisprototype.cli.irradiance.diffuse.transmission_function import (
    get_diffuse_transmission_function_series,
)
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_irradiance_series,
    rich_help_panel_toolbox,
)
from pvgisprototype.cli.typer.group import OrderCommands

app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help="Calculate the diffuse irradiance incident on a surface",
)
app.command(
    name="n-terms",
    no_args_is_help=True,
    help="N Calculate the N term for the diffuse sky irradiance function for a period of time",
    rich_help_panel=rich_help_panel_toolbox,
)(get_term_n_series)
app.command(
    name="sky-irradiances",
    no_args_is_help=True,
    help="⇊ Calculate the diffuse sky irradiance for a period of time",
    rich_help_panel=rich_help_panel_toolbox,
)(get_diffuse_sky_irradiance_series)
app.command(
    name="transmission-function",
    no_args_is_help=True,
    help="⇝ Calculate the diffuse transmission function over a series of linke turbidity factors",
    rich_help_panel=rich_help_panel_toolbox,
)(get_diffuse_transmission_function_series)
app.command(
    name="diffuse-altitude-coefficients",
    no_args_is_help=True,
    help="☀∡ Calculate the diffuse solar altitude coefficients",
    rich_help_panel=rich_help_panel_toolbox,
)(get_diffuse_solar_altitude_coefficients_series)
app.command(
    name="diffuse-altitude",
    no_args_is_help=True,
    help="☀∡ Calculate diffuse solar altitude angle time series",
    rich_help_panel=rich_help_panel_toolbox,
)(get_diffuse_solar_altitude_function_series)
app.command(
    name="horizontal",
    no_args_is_help=True,
    help="☀∡ Estimate the diffuse horizontal irradiance over a period of time [red]Not Complete[/red]",
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_diffuse_horizontal_irradiance_series)
app.command(
    name="inclined",
    no_args_is_help=True,
    help="☀∡ Calculate the diffuse irradiance incident on a surface over a period of time",
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_diffuse_inclined_irradiance_series)
app.command(
    name="horizontal-from-external-series",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_diffuse_horizontal_from_global_and_direct_irradiance)
