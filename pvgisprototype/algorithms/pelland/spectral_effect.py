#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from pvgisprototype import SpectralFactorSeries
from pandas import DataFrame
from xarray import DataArray
from pvgisprototype.constants import (
    SPECTRAL_FACTOR_COLUMN_NAME,
    SPECTRAL_FACTOR_NAME,
    TITLE_KEY_NAME,
    UNITLESS,
)
from pvgisprototype.log import log_function_call, logger


@log_function_call
def calculate_spectral_factor_pelland(
    irradiance: DataArray,
    responsivity: DataFrame,
    reference_spectrum: DataFrame,
) -> DataFrame:
    """Calculate the spectral factor for each PV technology based on
    Pelland 2022.

    Notes
    -----
    Some Python source code shared via personal communication.

    """
    # Verify the reference spectrum is valid (no zero or near-zero values) ?
    # if (reference_spectrum <= 0).any():
    #     raise ValueError(
    #         "The reference spectrum contains zero or negative values, which are invalid."
    #     )
    # else:
    #     print(f'Reference spectrum input : {reference_spectrum}')

    # Align wavelengths (columns) between dataframes
    # if not isinstance(irradiance, DataFrame):
    #     irradiance = irradiance.to_dataframe()
    # wavelengths = irradiance.columns.intersection(responsivity.index).intersection(
    #     reference_spectrum.columns
    # )
    import numpy

    logger.debug(
        f"Wavelengths in `irradiance` input : {irradiance.center_wavelength.values}",
    )
    logger.debug(
        f"Wavelengths in `responsivity` input : {responsivity}",
    )
    logger.debug(
        f"Wavelengths in `reference_spectrum` input : {reference_spectrum.columns}"
    )

    # Common wavelength range
    common_wavelengths = numpy.intersect1d(
        irradiance.center_wavelength.values,
        numpy.intersect1d(responsivity.center_wavelength, reference_spectrum.columns),
    )
    logger.debug(
        f"Intersection of wavelengths across input data : {common_wavelengths}"
    )

    # in Pelland : useful reference spectrum > average over the reference spectrum
    responsivity_selected = responsivity.sel(center_wavelength=common_wavelengths)
    logger.debug(f"Selected responsivity data : {responsivity_selected}")

    reference_spectrum_selected = reference_spectrum.loc["global", common_wavelengths]
    logger.debug(f"Selected reference spectrum data : {reference_spectrum_selected}")

    # in Pelland 2022 : useful fraction of reference spectrum
    reference_current_density = (
        responsivity_selected * reference_spectrum_selected
    ).sum() / reference_spectrum_selected.sum()
    logger.debug(
        f"Reference Current Density : {reference_current_density}",
        alt=f"[bold][yellow]Reference[/yellow] current density[/bold] : {reference_current_density}",
    )

    # useful irradiance (time-varying)
    irradiance_selected = irradiance.sel(center_wavelength=common_wavelengths)
    logger.debug(f"Selected irradiance data : {irradiance_selected}")
    sum_of_responsivity_by_irradiance = (
        responsivity_selected * irradiance_selected
    ).sum(dim="center_wavelength")
    logger.debug(
        f"Sum of responsivity * irradiance : {sum_of_responsivity_by_irradiance}"
    )
    sum_of_irradiance = (irradiance_selected).sum(dim="center_wavelength")
    logger.debug(f"Sum of irradiance : {sum_of_irradiance}")

    observed_current_density = (responsivity_selected * irradiance_selected).sum(
        dim="center_wavelength"
    ) / irradiance_selected.sum(dim="center_wavelength")
    logger.debug(f"Current Density of Observed Irradiance : {observed_current_density}")

    spectral_factor = observed_current_density / reference_current_density
    logger.debug(f"Spectral factor = {spectral_factor}")

    components_container = {
        "Metadata": lambda: {},
        "Spectral factor": lambda: {
            TITLE_KEY_NAME: SPECTRAL_FACTOR_NAME,
            SPECTRAL_FACTOR_COLUMN_NAME: spectral_factor.to_numpy(),
        },  # if verbose > 0 else {},
        "Inputs": lambda: {
            "Irradiance": irradiance,
            "Responsivity": responsivity,
            "Reference spectrum": reference_spectrum,
        },
        "Intermediate quantities": lambda: {
            "Common spectral wavelengths": common_wavelengths,
            "Selected spectral responsivity": responsivity_selected,
            "Selected observed irradiance": irradiance_selected,
            "Selected reference spectrum": reference_spectrum_selected,
        },
        "Sum of quantities": lambda: {
            "Sum of Irradiance": sum_of_irradiance,
            "Sum of responsivity by irradiance": sum_of_responsivity_by_irradiance,
            "Sum of Reference spectrum": reference_spectrum.sum(),
        },
        # "Energy" : lambda: {
        #     'Reference energy': total_reference_energy,
        #     'Observed energy': total_observed_energy,
        #     },
        "Current density": lambda: {
            "Reference current": reference_current_density,
            "Observed current": observed_current_density,
        },
        # if verbose > 1
        # else {},
    }
    components = {}
    for _, component in components_container.items():
        components.update(component())

    return SpectralFactorSeries(
        value=spectral_factor.to_numpy(),
        unit=UNITLESS,
        spectral_factor_algorithm="Pelland 2022",
        components=components,
    )
