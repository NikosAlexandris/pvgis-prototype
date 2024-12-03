from typing import Annotated

from numpy import ndarray

from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.api.irradiance.diffuse.altitude import (
    calculate_diffuse_transmission_function_series,
)
from pvgisprototype.cli.typer.linke_turbidity import (
    typer_argument_linke_turbidity_factor,
)
from pvgisprototype.log import log_function_call


@log_function_call
def get_diffuse_transmission_function_series(
    linke_turbidity_factor_series: Annotated[
        LinkeTurbidityFactor, typer_argument_linke_turbidity_factor
    ],
    verbose: int = 0,
) -> ndarray:
    """Diffuse transmission function over a period of time"""
    diffuse_transmission_series = calculate_diffuse_transmission_function_series(
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        verbose=verbose,
    )

    print(diffuse_transmission_series)
