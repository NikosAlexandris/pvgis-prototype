import typer
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_performance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_performance_toolbox
from pvgisprototype.cli.power.broadband import app as broadband
from pvgisprototype.cli.power.spectral import app as spectral
from pvgisprototype.cli.power.spectral_mismatch import app as spectral_factor
from pvgisprototype.cli.power.spectral_mismatch import app as spectral_mismatch
from pvgisprototype.cli.power.average_photon_energy import app as average_photon_energy
from pvgisprototype.cli.documentation import A_PRIMER_ON_PHOTOVOLTAIC_PERFORMANCE


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    # help=f":electric_plug: Estimate the photovoltaic power or aggregated energy production of a PV system over a time series based on solar irradiance and ambient temperature [bold green]Prototype[/bold green]",
    help=f":electric_plug: Estimate the performance of a photovoltaic system over a time series",
)
app.add_typer(
    broadband,
    name="broadband",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance,
)
app.add_typer(
    spectral,
    name="spectral",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance,
)
@app.command(
    'intro',
    no_args_is_help=False,
    help='A short primer on the performance of a photovoltaic system',
    rich_help_panel=rich_help_panel_performance_toolbox,
 )
def intro():
    """A short introduction on photovoltaic performance"""
    introduction = """
    [underline]The performance of a photovoltaic (PV) system[/underline] is ...
    """
    note = """
    PVGIS can estimate the performance of a series of photovoltaic technologies using either [magenta]broadband[/magenta] or [magenta]spectrally resolved[/magenta] irradiance data.
    """
    from rich.panel import Panel
    note_in_a_panel = Panel(
        "[italic]{}[/italic]".format(note),
        title="[bold cyan]Note[/bold cyan]",
        width=78,
    )
    from rich.console import Console
    console = Console()
    # introduction.wrap(console, 30)
    console.print(introduction)
    console.print(note_in_a_panel)
    console.print(A_PRIMER_ON_PHOTOVOLTAIC_PERFORMANCE)
app.add_typer(
    average_photon_energy,
    name="ape",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance_toolbox,
)
app.add_typer(
    spectral_factor,
    name="spectral-factor",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance_toolbox,
)
app.add_typer(
    spectral_mismatch,
    name="spectral-mismatch",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_performance_toolbox,
)
