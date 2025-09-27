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
from typing import List

from numpy import array as numpy_array

from pvgisprototype.api.irradiance.diffuse.altitude import calculate_term_n_series


def get_term_n_series(
    kb_series: List[float],
    verbose: int = 0,
):
    """Command line interface to calculate_term_n_series()

    Define the N term for a period of time

    Parameters
    ----------
    kb_series: float
        Direct to extraterrestrial irradiance ratio

    Returns
    -------
    N: float
        The N term
    """
    term_n_series = calculate_term_n_series(
        kb_series=numpy_array(kb_series),
        verbose=verbose,
    )

    print(term_n_series)
