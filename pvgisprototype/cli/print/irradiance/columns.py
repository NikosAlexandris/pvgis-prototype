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
from numpy import nansum, nanmean, ndarray, full
from rich.console import RenderableType
from rich.text import Text
from pvgisprototype.api.utilities.conversions import round_float_values
from pvgisprototype.cli.print.irradiance.keys import (
        KEYS_TO_EXCLUDE,
        KEYS_TO_SUM,
        KEYS_TO_AVERAGE,
        )


def add_key_table_columns(
    table,
    dictionary,
    timestamps,
    rounding_places,
    keys_to_sum: set = KEYS_TO_SUM,
    keys_to_average: set = KEYS_TO_AVERAGE,
    keys_to_exclude: set = KEYS_TO_EXCLUDE,
) -> RenderableType:
    """
    Notes
    -----
    Important : the input `dictionary` is expected to be a flat one.

    """
    for key, value in dictionary.items():
        if key not in keys_to_exclude:

            # if single numeric or string, generate an array "of it" as long as the timestamps

            if isinstance(value, (float, int)):
                dictionary[key] = full(len(timestamps), value)

            if isinstance(value, str):
                dictionary[key] = full(len(timestamps), str(value))

            # add sum of value/s to the column footer

            if key in keys_to_sum:
                if (
                    isinstance(value, ndarray)
                    # and not isnan(value).all()
                    and value.dtype.kind in "if"
                ):
                    sum_of_key_value = Text(
                        str(round_float_values(nansum(value), rounding_places)),
                        # style="code purple",
                        style="bold purple",
                    )
                    table.add_column(
                        header=key,
                        footer=sum_of_key_value,  # Place the Sum in the footer
                        footer_style="white",
                        no_wrap=False,
                    )

            elif key in keys_to_average:
                if (
                    isinstance(value, ndarray) and value.dtype.kind in "if"
                ) | isinstance(value, float):
                    table.add_column(
                        header=key,
                        footer=Text(str(nanmean(value))),  # Mean of Key Value in the footer
                        footer_style="italic blue",
                        no_wrap=False,
                    )
            else:
                table.add_column(key, no_wrap=False)

    return table
