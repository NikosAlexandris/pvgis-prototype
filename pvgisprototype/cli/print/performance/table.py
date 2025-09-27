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
from pandas import DatetimeIndex, Timestamp
from rich.box import SIMPLE_HEAD
from rich.table import Table
from pvgisprototype.cli.print.sparklines import convert_series_to_sparkline
import numpy
from pvgisprototype.constants import (
    NET_EFFECT,
    REFLECTIVITY,
    SPECTRAL_EFFECT_NAME,
    SYSTEM_LOSS,
    TEMPERATURE_AND_LOW_IRRADIANCE_COLUMN_NAME,
)


def build_performance_table(
    frequency_label: str,
    quantity_style: str,
    value_style: str,
    unit_style: str,
    mean_value_unit_style: str,
    percentage_style: str,
    # reference_quantity_style,
) -> Table:
    """
    Setup the main performance table with appropriate columns.
    """
    table = Table(
        # title="Photovoltaic Performance",
        # caption="Detailed view of changes in photovoltaic performance.",
        show_header=True,
        header_style="bold magenta",
        # show_footer=True,
        # row_styles=["none", "dim"],
        box=SIMPLE_HEAD,
        highlight=True,
    )
    table.add_column(
        "Quantity",
        justify="left",
        style=quantity_style,  # style="magenta",
        no_wrap=True,
    )
    table.add_column(
        "Total",  # f"{SYMBOL_SUMMATION}",
        justify="right",
        style=value_style,  # style="cyan",
    )
    table.add_column(
        "Unit",
        justify="left",
        style=unit_style,  # style="magenta",
    )
    table.add_column(
        "%",
        justify="right",
        style=percentage_style,  # style="dim",
    )
    table.add_column(
        "of",
        justify="left",
        style="dim",  # style=reference_quantity_style)
    )
    table.add_column(f"{frequency_label} Sums", style="dim", justify="center")
    # table.add_column(f"{frequency_label} Mean", justify="right", style="white dim")#style=value_style)
    table.add_column("Mean", justify="right", style="white dim")  # style=value_style)
    table.add_column(
        "Unit",  # for Mean values
        justify="left",
        style=mean_value_unit_style,
    )

    table.add_column(
        "Variability", justify="right", style="dim"
    )  # New column for standard deviation
    table.add_column("Source", style="dim", justify="left")

    return table


def add_table_row(
    table,
    quantity,
    value,
    unit,
    mean_value,
    mean_value_unit,
    standard_deviation = None,
    percentage = None,
    reference_quantity = None,
    series: numpy.ndarray = numpy.array([]),
    timestamps: DatetimeIndex | Timestamp = Timestamp.now(),
    frequency: str = "YE",
    source: str | None = None,
    quantity_style = None,
    value_style: str = "cyan",
    unit_style: str = "cyan",
    mean_value_style: str = "cyan",
    mean_value_unit_style: str = "cyan",
    percentage_style: str = "dim",
    reference_quantity_style: str = "white",
    rounding_places: int = 1,
):
    """
    Adds a row to a table with automatic unit handling and optional percentage.

    Parameters
    ----------
    table :
                The table object to which the row will be added.
    quantity :
                The name of the quantity being added.
    value :
                The numerical value associated with the quantity.
    base_unit :
                The base unit of measurement for the value.
    percentage :
                Optional; the percentage change or related metric.
    reference_quantity :
                Optional; the reference quantity for the percentage.
    rounding_places :
                Optional; the number of decimal places to round the value.

    Notes
    -----
    - Round value if rounding_places specified.
    - Convert units from base_unit to a larger unit if value exceeds 1000.
    - Add row to specified table.

    """
    effects = {
        REFLECTIVITY,
        SPECTRAL_EFFECT_NAME,
        TEMPERATURE_AND_LOW_IRRADIANCE_COLUMN_NAME,
        SYSTEM_LOSS,
        NET_EFFECT,
    }

    if value is None or numpy.isnan(value):
        signed_value = "-"  # this _is_ the variable added in a row !
    else:
        if isinstance(value, (float, numpy.float32, numpy.float64, int, numpy.int32, numpy.int64)):
            styled_value = (
                f"[{value_style}]{value:.{rounding_places}f}"
                if value_style
                else f"{value:.{rounding_places}f}"
            )
            signed_value = (
                f"[{quantity_style}]+{styled_value}"
                if quantity in effects and value > 0
                else styled_value
            )
        else:
            raise TypeError(f"Unexpected type for value: {type(value)}")

    # Need first the unstyled quantity for the `signed_value` :-)
    quantity = f"[{quantity_style}]{quantity}" if quantity_style else quantity

    # Mean value and unit
    mean_value = (
        f"[{mean_value_style}]{mean_value:.{rounding_places}f}"
        if mean_value_style
        else f"{mean_value:.{rounding_places}f}"
    )
    if standard_deviation:
        standard_deviation = (
            f"[{mean_value_style}]{standard_deviation:.{rounding_places}f}"
            if mean_value_style
            else f"{standard_deviation:.{rounding_places}f }"
        )
    else:
        standard_deviation = ""

    # Style the unit
    unit = f"[{unit_style}]{unit}" if unit_style else unit

    # Get the reference quantity
    reference_quantity = (
        f"[{reference_quantity_style}]{reference_quantity}"
        if reference_quantity_style
        else reference_quantity
    )

    # Build the sparkline
    sparkline = (
        convert_series_to_sparkline(series, timestamps, frequency)
        if series.size > 0
        else ""
    )

    # Prepare the basic row data structure
    row = [quantity, signed_value, unit]

    # Add percentage and reference quantity if applicable
    if percentage is not None:
        # percentage = f"[red]{percentage:.{rounding_places}f}" if percentage < 0 else f"[{percentage_style}]{percentage:.{rounding_places}f}"
        percentage = (
            f"[red bold]{percentage:.{rounding_places}f}"
            if percentage < 0
            else f"[green bold]+{percentage:.{rounding_places}f}"
        )
        row.extend([f"{percentage}"])
        if reference_quantity:
            row.extend([reference_quantity])
        else:
            row.extend([""])
    else:
        row.extend(["", ""])
    if sparkline:
        row.extend([sparkline])
    if mean_value:
        if not sparkline:
            row.extend([""])
        row.extend([mean_value, mean_value_unit, (standard_deviation)])
    else:
        row.extend([""])
    if source:
        row.extend([source])

    # table.add_row(
    #     quantity,
    #     value,
    #     unit,
    #     percentage,
    #     reference_quantity,
    #     style=quantity_style
    # )
    table.add_row(*row)


