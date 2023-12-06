import typer
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.algorithms.pvis.average_photon_energy import calculate_average_photon_energy
from pvgisprototype.algorithms.pvis.constants import ELECTRON_CHARGE
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_performance_toolbox


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f":electric_plug: Estimate the average photon energy (APE)",
)


@app.command(
    'ape',
    no_args_is_help=True,
    help=f"Estimate the average photon energy (APE)",
    rich_help_panel=rich_help_panel_performance_toolbox,
)
def average_photon_energy(  # series ?
    global_irradiance_series_up_to_1050,
    photon_flux_density, # number_of_photons_up_to_1050 ?
    electron_charge = ELECTRON_CHARGE,
):
    """
    The Average Photon Energy (APE) characterises the energetic distribution
    in an irradiance spectrum. It is calculated by dividing the irradiance
    [W/m² or eV/m²/sec] by the photon flux density [number of photons/m²/sec].
    [1]_

    References
    ----------
    .. [1] Jardine, C.N. & Gottschalg, Ralph & Betts, Thomas & Infield, David.
      (2002). Influence of Spectral Effects on the Performance of Multijunction
      Amorphous Silicon Cells. to be published.
    """
    average_photon_energy = calculate_average_photon_energy(
        global_power_1050=global_irradiance_series_up_to_1050,
        photon_flux_density=photon_flux_density,
        electron_charge=ELECTRON_CHARGE,
    )

    print(average_photon_energy)
