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
from rich.box import SIMPLE_HEAD
from rich.console import Console
from rich.table import Table
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import DECLINATION_COLUMN_NAME, HOUR_ANGLE_COLUMN_NAME, SURFACE_TILT_COLUMN_NAME, UNITS_COLUMN_NAME


def print_hour_angle_table(
    latitude,
    rounding_places,
    surface_tilt=None,
    declination=None,
    hour_angle=None,
    units=None,
) -> None:
    """ """
    latitude = round_float_values(latitude, rounding_places)
    # rounded_table = round_float_values(table, rounding_places)
    surface_tilt = round_float_values(surface_tilt, rounding_places)
    declination = round_float_values(declination, rounding_places)
    hour_angle = round_float_values(hour_angle, rounding_places)

    columns = ["Latitude", "Event"]
    if surface_tilt is not None:
        columns.append(SURFACE_TILT_COLUMN_NAME)
    if declination is not None:
        columns.append(DECLINATION_COLUMN_NAME)
    if hour_angle is not None:
        columns.append(HOUR_ANGLE_COLUMN_NAME)
    columns.append(UNITS_COLUMN_NAME)

    table = Table(
        *columns,
        box=SIMPLE_HEAD,
        show_header=True,
        header_style="bold magenta",
    )

    row = [str(latitude), "Event"]
    if surface_tilt is not None:
        row.append(str(surface_tilt))
    if declination is not None:
        row.append(str(declination))
    if hour_angle is not None:
        row.append(str(hour_angle))
    row.append(str(units))
    table.add_row(*row)

    Console().print(table)
