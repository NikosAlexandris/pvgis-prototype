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
from math import radians
from typing import Annotated, List

from numpy import array as numpy_array

from pvgisprototype.api.irradiance.diffuse.altitude import (
    calculate_diffuse_sky_irradiance_series,
)
from pvgisprototype.cli.typer.irradiance import typer_argument_term_n_series
from pvgisprototype.cli.typer.position import typer_argument_surface_tilt
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.log import log_function_call


@log_function_call
def get_diffuse_sky_irradiance_series(
    n_series: Annotated[
        List[float], typer_argument_term_n_series
    ],  # Needs a callback to parse list of input values !?
    surface_tilt: Annotated[float | None, typer_argument_surface_tilt] = radians(
        SURFACE_TILT_DEFAULT
    ),
):
    """Calculate the diffuse sky irradiance

    The diffuse sky irradiance function F(γN) depends on the surface tilt `γN`
    (in radians)

    Parameters
    ----------
    surface_tilt: float (radians)
        The tilt (also referred to as : inclination or slope) angle of a solar
        surface

    n_series: float
        The term N

    Returns
    -------

    Notes
    -----
    Internally the function calculates first the dimensionless fraction of the
    sky dome viewed by a tilted (or inclined) surface `ri(γN)`.
    """
    sky_view_fraction_series = calculate_diffuse_sky_irradiance_series(
        n_series=numpy_array(n_series),
        surface_tilt=surface_tilt,
    )

    print(sky_view_fraction_series)
