import typer
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.cli.irradiance.introduction import solar_irradiance_introduction
# from pvgisprototype.cli.irradiance.effective import app as effective_irradiance
from pvgisprototype.cli.irradiance.shortwave.shortwave import app as global_irradiance
from pvgisprototype.cli.irradiance.direct.direct import app as direct_irradiance
from pvgisprototype.cli.irradiance.diffuse.diffuse import app as diffuse_irradiance
from pvgisprototype.cli.irradiance.reflected import app as reflected_irradiance
from pvgisprototype.cli.irradiance.extraterrestrial import get_extraterrestrial_normal_irradiance_time_series
from pvgisprototype.api.irradiance.loss import app as angular_loss_factor
from pvgisprototype.api.irradiance.limits import app as limits
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
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


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    # help=f":sun_with_face: Estimate the solar irradiance incident on a horizontal or inclined surface",
    help=f":sun_with_face: Estimate the solar irradiance incident on a solar surface",
)
app.command(
    name='introduction',
    help='A short primer on solar irradiance',
    no_args_is_help=False,
    rich_help_panel=rich_help_panel_introduction,
)(solar_irradiance_introduction)
# app.add_typer(
#     effective_irradiance,
#     name="effective",
#     help="Estimate the effective irradiance over a time series",
#     no_args_is_help=True,
#     rich_help_panel=rich_help_panel_irradiance_series,
# )
app.add_typer(
    global_irradiance,
    name="global",
    help=f"Estimate the global irradiance over a time series",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)
app.add_typer(
    direct_irradiance,
    name="direct",
    help=f'Estimate the direct irradiance over a period of time',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)
app.add_typer(
    diffuse_irradiance,
    name="diffuse",
    help=f'Estimate the diffuse irradiance over a period of time',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)
app.add_typer(
    reflected_irradiance,
    name="reflected",
    help=f'Calculate the clear-sky ground reflected irradiance over a period of time',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)
app.command(
    name="extraterrestrial",
    help=f"Calculate the extraterrestrial normal irradiance over a time series",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_irradiance_series,
)(get_extraterrestrial_normal_irradiance_time_series)
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
