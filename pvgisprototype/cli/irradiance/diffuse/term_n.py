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
