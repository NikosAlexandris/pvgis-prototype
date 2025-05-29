import typer

from pvgisprototype.cli.irradiance.shortwave.horizontal import (
    get_global_horizontal_irradiance_series,
)
from pvgisprototype.cli.irradiance.shortwave.inclined import (
    get_global_inclined_irradiance_series,
)
from pvgisprototype.cli.irradiance.shortwave.spectral import (
    get_spectrally_resolved_global_inclined_irradiance_series,
)
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_irradiance_series
from pvgisprototype.cli.typer.group import OrderCommands

app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=":sun_with_face:⤋ Estimate the global irradiance incident on a surface over a time series ",
)
app.command(
    name="horizontal",
    no_args_is_help=True,
    help="Calculate the broadband global horizontal irradiance over a time series",
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_global_horizontal_irradiance_series)
app.command(
    name="inclined",
    no_args_is_help=True,
    help="Calculate the broadband global inclined irradiance over a time series",
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_global_inclined_irradiance_series)
app.command(
    name="spectral",
    no_args_is_help=True,
    help="Calculate the spectrally resolved global inclined irradiance over a time series",
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_spectrally_resolved_global_inclined_irradiance_series)
