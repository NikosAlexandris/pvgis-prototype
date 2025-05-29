import typer
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.irradiance.extraterrestrial.normal import (
    get_extraterrestrial_normal_irradiance_series,
)
from pvgisprototype.cli.irradiance.extraterrestrial.horizontal import (
    get_extraterrestrial_horizontal_irradiance_series,
)
from pvgisprototype.constants import (
    EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_TYPER_HELP,
    EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_TYPER_HELP_SHORT,
    EXTRATERRESTRIAL_NORMAL_IRRADIANCE_TYPER_HELP,
    EXTRATERRESTRIAL_NORMAL_IRRADIANCE_TYPER_HELP_SHORT,
)
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_irradiance_series,
)


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help="⍖ Estimate the clear-sky extraterrestrial irradiance",
)
app.command(
    name="normal",
    help=EXTRATERRESTRIAL_NORMAL_IRRADIANCE_TYPER_HELP,
    short_help=EXTRATERRESTRIAL_NORMAL_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_extraterrestrial_normal_irradiance_series)
app.command(
    name="horizontal",
    help=EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_TYPER_HELP,
    short_help=EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_extraterrestrial_horizontal_irradiance_series)
