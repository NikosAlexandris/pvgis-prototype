"""
Temperature time series
"""

from pathlib import Path

from devtools import debug
from numpy import fromstring, ndarray, full
import typer
from typer import Context

from pvgisprototype import TemperatureSeries
from pvgisprototype.api.datetime.datetimeindex import generate_datetime_series
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_meteorological_series,
)
from pvgisprototype.cli.typer.path import validate_path
from pvgisprototype.constants import (
    DATA_TYPE_DEFAULT,
    SYMBOL_UNIT_TEMPERATURE,
    TEMPERATURE_DEFAULT,
)


def parse_temperature_series(
    temperature_input: int | str | Path,
) -> int | str | Path | ndarray | None:
    """
    Notes
    -----
    FIXME: Re-design ?

    """
    try:
        if isinstance(temperature_input, int):
            return temperature_input

        if isinstance(temperature_input, (str, Path)):
            path = Path(temperature_input)
            if path.exists():
                return path

        if isinstance(temperature_input, str):
            temperature_input_array = fromstring(temperature_input, sep=",")
            if temperature_input_array.size > 0:
                debug(locals())
                return temperature_input_array
            else:
                raise ValueError(
                    f"The input string '{temperature_input}' could not be parsed into valid spectral factors."
                )

    except ValueError as e:  # conversion to float failed
        raise ValueError(
                f"Error parsing input: {e}"
        )
        

def temperature_series_argument_callback(
    ctx: Context,
    temperature_series: TemperatureSeries,
):
    """ """
    if isinstance(temperature_series, Path):
        return validate_path(temperature_series)

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

    # How to use print(ctx.get_parameter_source('temperature_series')) ?
    # See : class click.core.ParameterSource(value)

    if (
        isinstance(temperature_series, int)
        and temperature_series == TEMPERATURE_DEFAULT
    ):
        dtype = ctx.params.get("dtype", DATA_TYPE_DEFAULT)
        temperature_series = full(len(timestamps), TEMPERATURE_DEFAULT, dtype=dtype)

    # at this point, temperature_series _should_ be an array !
    if temperature_series.size != len(timestamps):
        # Improve error message with useful hint/s ?
        raise ValueError(
            f"The number of temperature values ({temperature_series.size}) does not match the number of irradiance values ({len(timestamps)})."
        )

    return TemperatureSeries(value=temperature_series, unit=SYMBOL_UNIT_TEMPERATURE)


def temperature_series_option_callback(
    ctx: Context,
    temperature_series: TemperatureSeries,
):
    reference_series = ctx.params.get("irradiance_series")
    if (
        isinstance(temperature_series, int)
        and temperature_series == TEMPERATURE_DEFAULT
    ):
        dtype = ctx.params.get("dtype", DATA_TYPE_DEFAULT)
        temperature_series = full(
            len(reference_series), TEMPERATURE_DEFAULT, dtype=dtype
        )

    if temperature_series.size != len(reference_series):
        raise ValueError(
            f"The number of temperature values ({temperature_series.size}) does not match the number of irradiance values ({len(reference_series)})."
        )

    return TemperatureSeries(value=temperature_series, unit=SYMBOL_UNIT_TEMPERATURE)


temperature_typer_help = "Ambient temperature time series"

# typer_argument_temperature_time_series = typer.Argument(
#     help="Ambient temperature in Celsius degrees.",
#     rich_help_panel=rich_help_panel_time_series,
#     # default_factory=25,
# )

typer_argument_temperature_series = typer.Option(
    help=temperature_typer_help,
    # min=TEMPERATURE_MINIMUM,
    # max=TEMPERATURE_MAXIMUM,
    rich_help_panel=rich_help_panel_meteorological_series,
    # is_eager=True,
    parser=parse_temperature_series,
    callback=temperature_series_argument_callback,
    show_default=False,
)
typer_option_temperature_series = typer.Option(
    help=temperature_typer_help,
    # min=TEMPERATURE_MINIMUM,
    # max=TEMPERATURE_MAXIMUM,
    rich_help_panel=rich_help_panel_meteorological_series,
    # is_eager=True,
    parser=parse_temperature_series,
    callback=temperature_series_option_callback,
)
