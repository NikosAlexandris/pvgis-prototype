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
