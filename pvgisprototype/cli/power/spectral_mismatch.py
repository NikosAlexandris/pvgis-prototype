import typer
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.algorithms.pvis.spectral_factor import calculate_minimum_spectral_mismatch
from pvgisprototype.algorithms.pvis.spectral_factor import calculate_spectral_factor
from pvgisprototype.algorithms.pvis.constants import ELECTRON_CHARGE
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_performance_toolbox


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Estimate the spectral factor or spectral mismatch [green]Prototype[/green]",
)


@app.command(
    'spectral-factor',
    no_args_is_help=True,
    help=f"Estimate the spectral factor",
    rich_help_panel=rich_help_panel_performance_toolbox,
)
def spectral_factor(
    minimum_spectral_mismatch,
    global_total_power,
    standard_conditions_response,
):  # series ?
    """ """
    spectral_factor = calculate_spectral_factor(
        minimum_spectral_mismatch=minimum_spectral_mismatch,
        global_total_power=global_total_power,
        standard_conditions_response=standard_conditions_response,
    )

    return spectral_factor


@app.command(
    'spectral-mismatch',
    no_args_is_help=True,
    help=f"Estimate the spectral mismatch",
    rich_help_panel=rich_help_panel_performance_toolbox,
)
def spectral_mismatch(  # series ?
    response_wavelengths,
    spectral_response,
    number_of_junctions: int,
    spectral_power_density,#=spectral_power_density_up_to_1050,
):
    """
    """
    (
        minimum_spectral_mismatch,
        minimum_junction,
    ) = calculate_minimum_spectral_mismatch(
        response_wavelengths=response_wavelengths,
        spectral_response=spectral_response,
        number_of_junctions=number_of_junctions,
        spectral_power_density=spectral_power_density,
    )
