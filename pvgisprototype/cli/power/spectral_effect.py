from pvgisprototype.algorithms.pvis.spectral_factor import (
    calculate_minimum_spectral_mismatch,
    calculate_spectral_factor,
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


def spectral_mismatch(  # series ?
    response_wavelengths,
    spectral_response,
    number_of_junctions: int,
    spectral_power_density,  # =spectral_power_density_up_to_1050,
):
    """ """
    (
        minimum_spectral_mismatch,
        minimum_junction,
    ) = calculate_minimum_spectral_mismatch(
        response_wavelengths=response_wavelengths,
        spectral_response=spectral_response,
        number_of_junctions=number_of_junctions,
        spectral_power_density=spectral_power_density,
    )
