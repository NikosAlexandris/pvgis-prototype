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
"""
Temperature time series
"""

from pathlib import Path

from numpy import fromstring, ndarray, full
import typer
from typer import Context

from pvgisprototype import RelativeHumiditySeries
from pvgisprototype.api.datetime.datetimeindex import generate_datetime_series
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_meteorological_series,
)
from pvgisprototype.cli.typer.path import validate_path
from pvgisprototype.constants import (
    DATA_TYPE_DEFAULT,
    SYMBOL_UNIT_TEMPERATURE,
    RELATIVE_HUMIDITY_DEFAULT,
)


def parse_relative_humidity_series(
    relative_humidity_input: int | str | Path,
) -> int | str | Path | ndarray | None:
    """
    Notes
    -----
    FIXME: Re-design ?

    """
    try:
        if isinstance(relative_humidity_input, int):
            return relative_humidity_input

        if isinstance(relative_humidity_input, (str, Path)):
            path = Path(relative_humidity_input)
            if path.exists():
                return path

        if isinstance(relative_humidity_input, str):
            relative_humidity_input_array = fromstring(relative_humidity_input, sep=",")
            if relative_humidity_input_array.size > 0:
                return relative_humidity_input_array
            else:
                raise ValueError(
                    f"The input string '{relative_humidity_input}' could not be parsed into valid spectral factors."
                )

    except ValueError as e:  # conversion to float failed
        raise ValueError(
                f"Error parsing input: {e}"
        )
        

def relative_humidity_series_argument_callback(
    ctx: Context,
    relative_humidity_series: RelativeHumiditySeries,
):
    """ """
    if isinstance(relative_humidity_series, Path):
        return validate_path(relative_humidity_series)

    timestamps = ctx.params.get("timestamps", None)
    if timestamps is None:
        start_time = ctx.params.get("start_time")
        end_time = ctx.params.get("end_time")
        periods = ctx.params.get("periods", None)
        from pvgisprototype.constants import TIMESTAMPS_FREQUENCY_DEFAULT

        frequency = (
            ctx.params.get("frequency", TIMESTAMPS_FREQUENCY_DEFAULT)
            if not periods
            else None
        )
        if start_time is not None and end_time is not None:
            timestamps = generate_datetime_series(
                start_time=start_time,
                end_time=end_time,
                periods=periods,
                frequency=frequency,
                timezone=ctx.params.get("timezone"),
                name=ctx.params.get("datetimeindex_name", None),
            )
        else:
            from pvgisprototype.log import logger

            logger.error("Did you provide both a start and an end time ?")

    # How to use print(ctx.get_parameter_source('relative_humidity_series')) ?
    # See : class click.core.ParameterSource(value)

    if (
        isinstance(relative_humidity_series, int)
        and relative_humidity_series == RELATIVE_HUMIDITY_DEFAULT
    ):
        dtype = ctx.params.get("dtype", DATA_TYPE_DEFAULT)
        relative_humidity_series = full(len(timestamps), RELATIVE_HUMIDITY_DEFAULT, dtype=dtype)

    # at this point, relative_humidity_series _should_ be an array !
    if relative_humidity_series.size != len(timestamps):
        # Improve error message with useful hint/s ?
        raise ValueError(
            f"The number of temperature values ({relative_humidity_series.size}) does not match the number of irradiance values ({len(timestamps)})."
        )

    return RelativeHumiditySeries(value=relative_humidity_series, unit=SYMBOL_UNIT_TEMPERATURE)


def relative_humidity_series_option_callback(
    ctx: Context,
    relative_humidity_series: RelativeHumiditySeries,
):
    reference_series = ctx.params.get("irradiance_series")
    if (
        isinstance(relative_humidity_series, int)
        and relative_humidity_series == RELATIVE_HUMIDITY_DEFAULT
    ):
        dtype = ctx.params.get("dtype", DATA_TYPE_DEFAULT)
        relative_humidity_series = full(
            len(reference_series), RelativeHumiditySeries().average_relative_humidity, dtype=dtype
        )

    if relative_humidity_series.size != len(reference_series):
        raise ValueError(
            f"The number of temperature values ({relative_humidity_series.size}) does not match the number of irradiance values ({len(reference_series)})."
        )

    return RelativeHumiditySeries(value=relative_humidity_series, unit=SYMBOL_UNIT_TEMPERATURE)


relative_humidity_typer_help = "Ambient temperature time series"

# typer_argument_relative_humidity_time_series = typer.Argument(
#     help="Ambient temperature in Celsius degrees.",
#     rich_help_panel=rich_help_panel_time_series,
#     # default_factory=25,
# )

typer_argument_relative_humidity_series = typer.Argument(
    help=relative_humidity_typer_help,
    # min=RELATIVE_HUMIDITY_MINIMUM,
    # max=RELATIVE_HUMIDITY_MAXIMUM,
    rich_help_panel=rich_help_panel_meteorological_series,
    # is_eager=True,
    parser=parse_relative_humidity_series,
    callback=relative_humidity_series_argument_callback,
    show_default=False,
)
typer_option_relative_humidity_series = typer.Option(
    help=relative_humidity_typer_help,
    # min=RELATIVE_HUMIDITY_MINIMUM,
    # max=RELATIVE_HUMIDITY_MAXIMUM,
    rich_help_panel=rich_help_panel_meteorological_series,
    # is_eager=True,
    parser=parse_relative_humidity_series,
    # callback=relative_humidity_series_option_callback,
    callback=relative_humidity_series_argument_callback,
)
