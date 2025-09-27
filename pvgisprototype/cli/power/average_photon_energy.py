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
from pvgisprototype.algorithms.hofierka.spectrum.average_photon_energy import (
    calculate_average_photon_energy,
)
from pvgisprototype.algorithms.hofierka.constants import ELECTRON_CHARGE
from pvgisprototype.log import log_function_call


@log_function_call
def average_photon_energy(  # series ?
    global_irradiance_series_up_to_1050,
    photon_flux_density,  # number_of_photons_up_to_1050 ?
    electron_charge=ELECTRON_CHARGE,
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
