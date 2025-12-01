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
from numpy import full
from rich.box import SIMPLE_HEAD
from rich.console import Console
from rich.table import Table
from rich.text import Text

from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.constants import (
    NOT_AVAILABLE,
    ROUNDING_PLACES_DEFAULT,
    SYMBOL_LOSS,
    TITLE_KEY_NAME,
)


def style_value(value, style_if_negative="dim"):
    if value is not None:
        if value < 0:
            return f"[{style_if_negative}]{value}[/]"
        else:
            return str(value)
    return None


def print_table(headers: List[str], data: List[List[str]]) -> None:
    """Create and print a table with provided headers and data."""
    table = Table(show_header=True, header_style="bold magenta", box=SIMPLE_HEAD)
    for header in headers:
        table.add_column(header)

    for row_data in data:
        table.add_row(*row_data)

    Console().print(table)


def print_quantity_table(
    dictionary: dict = dict(),
    title: str = "Series",
    main_key: str | None = None,
    rounding_places: int = ROUNDING_PLACES_DEFAULT,
    verbose=1,
    index: bool = False,
) -> None:
    table = Table(title=title, box=SIMPLE_HEAD)

    if index:
        table.add_column("Index")

    # remove the 'Title' entry! ---------------------------------------------
    dictionary.pop(TITLE_KEY_NAME, NOT_AVAILABLE)
    # ------------------------------------------------------------- Important

    # # base columns
    # if verbose > 0:

    # additional columns based dictionary keys
    for key in dictionary.keys():
        if dictionary[key] is not None:
            table.add_column(key)

    if not main_key:  # consider the 1st key of having the "valid" number of values
        main_key = list(dictionary.keys())[0]

    # Convert single float or int values to arrays of the same length as the "main' key
    for key, value in dictionary.items():
        if isinstance(value, (float, int)):
            dictionary[key] = full(len(dictionary[main_key]), value)

        if isinstance(value, str):
            dictionary[key] = full(len(dictionary[main_key]), str(value))

    # Zip series
    zipped_series = zip(*dictionary.values())

    # Populate table
    index_counter = 1
    if verbose:
        for values in zipped_series:
            row = []

            if index:
                row.append(str(index_counter))
                index_counter += 1

            for idx, (column_name, value) in enumerate(zip(dictionary.keys(), values)):
                if idx == 0:  # assuming after 'Time' is the value of main interest
                    bold_value = Text(
                        str(round_float_values(value, rounding_places)), style="bold"
                    )
                    row.append(bold_value)
                else:
                    if not isinstance(value, str):
                        if SYMBOL_LOSS in column_name:
                            red_value = Text(
                                str(round_float_values(value, rounding_places)),
                                style="bold red",
                            )
                            row.append(red_value)
                        else:
                            row.append(str(round_float_values(value, rounding_places)))
                    else:
                        row.append(value)
            table.add_row(*row)

        Console().print(table)


def determine_frequency(timestamps):
    """ """
    # First, get the "frequency" from the timestamps
    time_groupings = {
        "YE": "Yearly",
        "S": "Seasonal",
        "ME": "Monthly",
        "W": "Weekly",
        "D": "Daily",
        "3h": "3-Hourly",
        "h": "Hourly",
        "min": "Minutely",
        "8min": "8-Minutely",
    }
    if timestamps.year.unique().size > 1:
        frequency = "YE"
    elif timestamps.month.unique().size > 1:
        frequency = "ME"
    elif timestamps.to_period().week.unique().size > 1:
        frequency = "W"
    elif timestamps.day.unique().size > 1:
        frequency = "D"
    elif timestamps.hour.unique().size > 1:
        if timestamps.hour.unique().size < 17:  # Explain Me !
            frequency = "h"
        else:
            frequency = "3h"
    elif timestamps.minute.unique().size < 17:  # Explain Me !
        frequency = "min"
    else:
        frequency = "8min"  # by 8 characters for a sparkline if timestamps > 64 min
    frequency_label = time_groupings[frequency]

    return frequency, frequency_label
