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
from pvgisprototype.cli.typer.location import (
    typer_argument_latitude,
    typer_argument_longitude,
)


def get_horizon(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
):
    """Calculate the entire horizon angle height (in radians) around a single point from a digital elevation model

    Notes:
        - Based on the original C program `horizon_out`
        - Variable, Typr, Range, Default, Notes
        - lat, float, [-90, 90], -, Latitude in decimal degrees, south is negative. Required
        - lon, float, [-180, 180], - , Longitude in decimal degrees, west is negative. Required
        - userhorizon, list, List of float values ranging in [0, 90] separated by comma (CSV) (length < =365), -, Height of the horizon at equidistant directions around the point of interest, in degrees.
          Starting at north and moving clockwise. The series 0, 10, 20, 30, 40,
          15, 25, 5 would mean the horizon height is 0° due north, 10° for
          north-east, 20° for east, 30° for south-east, and so on. Optional,
          Depends on `userhorizon=1`,
        - outputformat, str, [csv, basic, json], csv, Output format. csv: CSV with text explanations, basic: CSV. Optional
        - browser, bool, 0, 1, 0, Setting browser=1 and accessing the service through a web browser, will save the retrieved data to a file. Optional
    """
    pass


