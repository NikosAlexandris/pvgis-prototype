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

## Linke turbidity

import numpy as np
import typer
from typer import Context

from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_atmospheric_properties,
)
from pvgisprototype.constants import (
    DATA_TYPE_DEFAULT,
    LINKE_TURBIDITY_DEFAULT,
    LINKE_TURBIDITY_MAXIMUM,
    LINKE_TURBIDITY_MINIMUM,
    LINKE_TURBIDITY_UNIT,
)


def parse_linke_turbidity_factor_series(
    linke_turbidity_factor_input: str,
):
    """
    Notes
    -----
    FIXME: Re-design ?

    """
    try:
        if isinstance(linke_turbidity_factor_input, int):
            return linke_turbidity_factor_input

        if (
            isinstance(linke_turbidity_factor_input, str)
            and linke_turbidity_factor_input == "0"
        ):
            linke_turbidity_factor_input = np.array([int(linke_turbidity_factor_input)])

        elif isinstance(linke_turbidity_factor_input, str):
            linke_turbidity_factor_input = np.fromstring(
                linke_turbidity_factor_input, sep=","
            )

        return linke_turbidity_factor_input

    except ValueError as e:  # conversion to float failed
        print(f"Error parsing input: {e}")
        return None


def linke_turbidity_factor_callback(
    ctx: Context,
    linke_turbidity_factor_series: np.array,
):
    if linke_turbidity_factor_series is None:
        return np.ndarray([])

    else:
        timestamps = ctx.params.get("timestamps")
        dtype = ctx.params.get("dtype", DATA_TYPE_DEFAULT)
        return LinkeTurbidityFactor(
            value=np.array([LINKE_TURBIDITY_DEFAULT for _ in timestamps], dtype=dtype),
            unit=LINKE_TURBIDITY_UNIT,
        )


linke_turbidity_factor_typer_help = (
    "Ratio of total to Rayleigh optical depth measuring atmospheric turbidity"
)
typer_argument_linke_turbidity_factor = typer.Argument(
    help=linke_turbidity_factor_typer_help,
    min=LINKE_TURBIDITY_MINIMUM,
    max=LINKE_TURBIDITY_MAXIMUM,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    parser=parse_linke_turbidity_factor_series,
    callback=linke_turbidity_factor_callback,
    # default_factory=LINKE_TURBIDITY_DEFAULT,
    show_default=False,
)
typer_option_linke_turbidity_factor = typer.Option(
    help=linke_turbidity_factor_typer_help,
    min=LINKE_TURBIDITY_MINIMUM,
    max=LINKE_TURBIDITY_MAXIMUM,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    parser=parse_linke_turbidity_factor_series,
    callback=linke_turbidity_factor_callback,
    # default_factory=LINKE_TURBIDITY_DEFAULT,
)

linke_turbidity_factor_series_typer_help = (
    "Ratio series of total to Rayleigh optical depth measuring atmospheric turbidity"
)
typer_option_linke_turbidity_factor_series = typer.Option(
    help=linke_turbidity_factor_typer_help,
    # min=LINKE_TURBIDITY_MINIMUM,
    # max=LINKE_TURBIDITY_MAXIMUM,
    parser=parse_linke_turbidity_factor_series,
    callback=linke_turbidity_factor_callback,
    rich_help_panel=rich_help_panel_atmospheric_properties,
    # default_factory=LINKE_TURBIDITY_DEFAULT,
)
