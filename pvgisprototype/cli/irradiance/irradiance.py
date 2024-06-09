import typer
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.irradiance.introduction import solar_irradiance_introduction
from pvgisprototype.cli.irradiance.shortwave.shortwave import app as global_irradiance
from pvgisprototype.cli.irradiance.direct.direct import app as direct_irradiance
from pvgisprototype.cli.irradiance.diffuse.diffuse import app as diffuse_irradiance
from pvgisprototype.cli.irradiance.reflected import get_ground_reflected_inclined_irradiance_series
from pvgisprototype.cli.irradiance.extraterrestrial import get_extraterrestrial_normal_irradiance_series
from pvgisprototype.cli.irradiance.reflectivity import app as reflectivity_factor
from pvgisprototype.cli.irradiance.limits import app as limits
from pvgisprototype.cli.messages import NOT_COMPLETE_CLI, NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_introduction
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_atmospheric_properties
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_earth_orbit
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_efficiency
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_surface_geometry
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_irradiance_series
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_time
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.constants import(
        GLOBAL_IRRADIANCE_TYPER_HELP_SHORT,
        GLOBAL_IRRADIANCE_TYPER_HELP,
        DIRECT_IRRADIANCE_TYPER_HELP_SHORT,
        DIRECT_IRRADIANCE_TYPER_HELP,
        DIFFUSE_IRRADIANCE_TYPER_HELP_SHORT,
        DIFFUSE_IRRADIANCE_TYPER_HELP,
        REFLECTED_IRRADIANCE_TYPER_HELP_SHORT,
        REFLECTED_IRRADIANCE_TYPER_HELP,
        EXTRATERRESTRIAL_IRRADIANCE_TYPER_HELP_SHORT,
        EXTRATERRESTRIAL_IRRADIANCE_TYPER_HELP,
        SYMBOL_IRRADIANCE,
        SYMBOL_IRRADIANCE_LIMITS,
        )


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"󱟿 Calculate the solar irradiance incident on a solar surface",
)
app.command(
    name='introduction',
    help='A short primer on solar irradiance',
    no_args_is_help=False,
    rich_help_panel=rich_help_panel_introduction,
)(solar_irradiance_introduction)
app.add_typer(
    global_irradiance,
    name="global",
    help=GLOBAL_IRRADIANCE_TYPER_HELP,
    short_help=GLOBAL_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)
app.add_typer(
    direct_irradiance,
    name="direct",
    help=DIRECT_IRRADIANCE_TYPER_HELP,
    short_help=DIRECT_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)
app.add_typer(
    diffuse_irradiance,
    name="diffuse",
    help=DIFFUSE_IRRADIANCE_TYPER_HELP,
    short_help=DIFFUSE_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)
app.command(
    name="reflected",
    help=REFLECTED_IRRADIANCE_TYPER_HELP,
    short_help=REFLECTED_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_ground_reflected_inclined_irradiance_series)
app.command(
    name="extraterrestrial",
    help=EXTRATERRESTRIAL_IRRADIANCE_TYPER_HELP,
    short_help=EXTRATERRESTRIAL_IRRADIANCE_TYPER_HELP_SHORT,
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_extraterrestrial_normal_irradiance_series)
app.add_typer(
    reflectivity_factor,
    name="reflectivity",
    help=f"⦟ Calculate the reflectivity effect factor for inclined irradiance components {NOT_COMPLETE_CLI}",
    short_help=f"⦟ Calculate the reflectivity effect factor {NOT_COMPLETE_CLI}",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    limits,
    name="limits",
    help=f"{SYMBOL_IRRADIANCE_LIMITS} Calculate physically possible irradiance limits",
    short_help=f"{SYMBOL_IRRADIANCE_LIMITS} Calculate physically possible irradiance limits",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
