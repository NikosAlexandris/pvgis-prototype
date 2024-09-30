import typer

from pvgisprototype.cli.performance.broadband import (
    photovoltaic_power_output_series,
    photovoltaic_power_output_series_from_multiple_surfaces,
)
from pvgisprototype.cli.performance.introduction import photovoltaic_performance_introduction
from pvgisprototype.cli.performance.spectral import spectral_photovoltaic_performance_analysis
from pvgisprototype.cli.performance.spectral_effect import spectral_factor
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_introduction,
    rich_help_panel_performance,
    rich_help_panel_spectral_factor,
)
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.constants import (
    SYMBOL_BROADBAND_IRRADIANCE,
    SYMBOL_INTRODUCTION,
    SYMBOL_SPECTRALLY_RESOLVED_IRRADIANCE,
)
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI


app = typer.Typer(
    cls=OrderCommands,
    # pretty_exceptions_short=True,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    # help=f":electric_plug: Estimate the photovoltaic power or aggregated energy production of a PV system over a time series based on solar irradiance and ambient temperature [bold green]Prototype[/bold green]",
    help=":electric_plug: Analyse the performance of a photovoltaic system over a time series",
)
app.command(
    name="introduction",
    help=f"{SYMBOL_INTRODUCTION} A short primer on the performance of a photovoltaic system",
    no_args_is_help=False,
    rich_help_panel=rich_help_panel_introduction,
)(photovoltaic_performance_introduction)
app.command(
    name="broadband",
    # help=f"Estimate the photovoltaic performance based on [bold]broadband irradiance[/bold], ambient temperature and wind speed",
    help=f"{SYMBOL_BROADBAND_IRRADIANCE} Estimate the photovoltaic power over a time series or an arbitrarily aggregated energy production of a PV system based on [bold]broadband irradiance[/bold], ambient temperature and wind speed",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance,
)(photovoltaic_power_output_series)
app.command(
    name="broadband-multi",
    # help=f"Estimate the photovoltaic performance based on [bold]broadband irradiance[/bold], ambient temperature and wind speed",
    help="Estimate the photovoltaic power over a time series or an arbitrarily aggregated energy production of a PV system based on [bold]broadband irradiance[/bold], ambient temperature and wind speed",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance,
)(photovoltaic_power_output_series_from_multiple_surfaces)
app.command(
    name="spectral",
    help=f"{SYMBOL_SPECTRALLY_RESOLVED_IRRADIANCE} Estimate the photovoltaic power over a time series or an arbitrarily aggregated energy production of a PV system based on [bold]spectrally resolved irradiance[/bold] incident on a solar surface, ambient temperature or wind speed {NOT_IMPLEMENTED_CLI}",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance,)(spectral_photovoltaic_performance_analysis)
# app.command(
#     name="spectral-factor",
#     help="Estimate the spectral factor",
#     no_args_is_help=True,
#     rich_help_panel=rich_help_panel_spectral_factor,
# )(spectral_factor)
# app.command(
#     name="spectral-mismatch",
#     help="Estimate the spectral mismatch",
#     no_args_is_help=True,
#     rich_help_panel=rich_help_panel_performance_toolbox,
# )(spectral_mismatch)
app.command(
    name="spectral-factor",
    help="Estimate the spectral factor",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_spectral_factor,
)(spectral_factor)
