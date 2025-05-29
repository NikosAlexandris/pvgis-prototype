import typer

from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.power.average_photon_energy import average_photon_energy
from pvgisprototype.cli.power.broadband import photovoltaic_power_output_series
from pvgisprototype.cli.power.broadband_bifacial import bifacial_photovoltaic_power_output_series
from pvgisprototype.cli.power.broadband_multiple_surfaces import photovoltaic_power_output_series_from_multiple_surfaces
from pvgisprototype.cli.power.efficiency import photovoltaic_efficiency_series
from pvgisprototype.cli.power.temperature import photovoltaic_module_temperature
from pvgisprototype.cli.power.introduction import photovoltaic_power_introduction
from pvgisprototype.cli.power.spectral import spectral_photovoltaic_power_output_series
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_introduction,
    rich_help_panel_performance,
    rich_help_panel_performance_toolbox,
)
from pvgisprototype.cli.typer.group import OrderCommands
from pvgisprototype.constants import (
    SYMBOL_BROADBAND_IRRADIANCE,
    SYMBOL_INTRODUCTION,
    SYMBOL_SPECTRALLY_RESOLVED_IRRADIANCE,
)

app = typer.Typer(
    cls=OrderCommands,
    # pretty_exceptions_short=True,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    # help=f":electric_plug: Estimate the photovoltaic power or aggregated energy production of a PV system over a time series based on solar irradiance and ambient temperature [bold green]Prototype[/bold green]",
    help=":electric_plug: Estimate the photovoltaic power over a time series",
)
app.command(
    name="introduction",
    help=f"{SYMBOL_INTRODUCTION} A short primer on photovoltaic power",
    no_args_is_help=False,
    rich_help_panel=rich_help_panel_introduction,
)(photovoltaic_power_introduction)
app.command(
    name="broadband",
    # help=f"Estimate the photovoltaic performance based on [bold]broadband irradiance[/bold], ambient temperature and wind speed",
    help=f"{SYMBOL_BROADBAND_IRRADIANCE} Estimate the photovoltaic power over a time series or an arbitrarily aggregated energy production of a PV system based on [bold]broadband irradiance[/bold], ambient temperature and wind speed",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance,
)(photovoltaic_power_output_series)
app.command(
    name="broadband-bifacial",
    # help=f"Estimate the photovoltaic performance based on [bold]broadband irradiance[/bold], ambient temperature and wind speed",
    help=f"{SYMBOL_BROADBAND_IRRADIANCE} Estimate the rear-side photovoltaic power over a time series or an arbitrarily aggregated energy production of a Bi-Facial PV system based on [bold]broadband irradiance[/bold], ambient temperature and wind speed",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance,
)(bifacial_photovoltaic_power_output_series)
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
    rich_help_panel=rich_help_panel_performance,
)(spectral_photovoltaic_power_output_series)
app.command(
    name="efficiency",
    help="Calculate the efficiency of a photovoltaic system",
    no_args_is_help=True,
    # context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
    rich_help_panel=rich_help_panel_performance_toolbox,
)(photovoltaic_efficiency_series)
app.command(
    name="temperature",
    help="Calculate the effect of temperature on the efficiency of a photovoltaic system [red]Not complete[/red]",
    no_args_is_help=True,
    # context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
    rich_help_panel=rich_help_panel_performance_toolbox,
)(photovoltaic_module_temperature)
app.command(
    name="photon-energy",  # "ape",
    help=":electric_plug: Estimate the average photon energy (APE)",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance_toolbox,
)(average_photon_energy)
