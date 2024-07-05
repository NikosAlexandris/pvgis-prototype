from typing import Annotated, List

from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.api.irradiance.diffuse.altitude import (
    calculate_diffuse_solar_altitude_coefficients_series,
    calculate_diffuse_solar_altitude_function_series,
)
from pvgisprototype.cli.typer.linke_turbidity import (
    typer_argument_linke_turbidity_factor,
    typer_option_linke_turbidity_factor_series,
)
from pvgisprototype.cli.typer.position import typer_argument_solar_altitude_series
from pvgisprototype.log import log_function_call


@log_function_call
def get_diffuse_solar_altitude_coefficients_series(
    linke_turbidity_factor_series: Annotated[
        LinkeTurbidityFactor, typer_argument_linke_turbidity_factor
    ],  #: np.ndarray,
    verbose: int = 0,
):
    """
    Vectorized function to calculate the diffuse solar altitude coefficients over a period of time.

    Parameters
    ----------
    - linke_turbidity_factor_series (List[LinkeTurbidityFactor] or LinkeTurbidityFactor):
      The Linke turbidity factors as a list of LinkeTurbidityFactor objects or a single object.

    Returns
    -------
    """
    diffuse_solar_altitude_coefficients_series = (
        calculate_diffuse_solar_altitude_coefficients_series(
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            verbose=verbose,
        )
    )

    print("a1, a2, a3")
    print(diffuse_solar_altitude_coefficients_series)


@log_function_call
def get_diffuse_solar_altitude_function_series(
    solar_altitude_series: Annotated[List[float], typer_argument_solar_altitude_series],
    linke_turbidity_factor_series: Annotated[
        LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series
    ],  #: np.ndarray,
    verbose: int = 0,
):
    """Diffuse solar altitude function Fd"""
    diffuse_solar_altitude_series = calculate_diffuse_solar_altitude_function_series(
        solar_altitude_series=solar_altitude_series,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
    )

    print(diffuse_solar_altitude_series)
