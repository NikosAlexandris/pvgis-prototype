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
