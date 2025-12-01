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
Wind speed
"""

from pathlib import Path

from numpy import ndarray, array, fromstring
import typer
from typer import Context

from pvgisprototype import WindSpeedSeries
from pvgisprototype.api.datetime.datetimeindex import generate_datetime_series
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_meteorological_series,
)
from pvgisprototype.cli.typer.path import validate_path
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    SYMBOL_UNIT_WIND_SPEED,
    WIND_SPEED_DEFAULT,
)


def parse_wind_speed_series(
    wind_speed_input: int | str | Path,
) -> int | str | Path | ndarray | None:
    """
    Notes
    -----
    FIXME: Re-design ?

    """
    try:
        if isinstance(wind_speed_input, int):
            return wind_speed_input

        if isinstance(wind_speed_input, (str, Path)):
            path = Path(wind_speed_input)
            if path.exists():
                return path

        if isinstance(wind_speed_input, str):
            wind_speed_input_array = fromstring(wind_speed_input, sep=",")
            if wind_speed_input_array.size > 0:
                return wind_speed_input_array
            else:
                raise ValueError(
                    f"The input string '{wind_speed_input}' could not be parsed into valid spectral factors."
                )

    except ValueError as e:  # conversion to float failed
        print(f"Error parsing input: {e}")
        return None

def wind_speed_series_argument_callback(
    ctx: Context,
    wind_speed_series: WindSpeedSeries,
):
    """ """
    if isinstance(wind_speed_series, Path):
        return validate_path(wind_speed_series)

    timestamps = ctx.params.get("timestamps", None)
    
    # If no timestamps in context yet, just return as-is
    # They'll be validated later in the actual command function
    if timestamps is None:
        return wind_speed_series
    
    # Only process if we have timestamps AND default value
    if isinstance(wind_speed_series, int) and wind_speed_series == WIND_SPEED_DEFAULT:
        from pvgisprototype.core.arrays import create_array

        dtype = ctx.params.get("dtype", DATA_TYPE_DEFAULT)
        array_backend = ctx.params.get("array_backend", ARRAY_BACKEND_DEFAULT)
        shape_of_array = timestamps.shape
        wind_speed_series = create_array(
            shape_of_array,
            dtype=dtype,
            init_method=WIND_SPEED_DEFAULT,
            backend=array_backend,
        )
        return WindSpeedSeries(value=wind_speed_series, unit=SYMBOL_UNIT_WIND_SPEED)
    
    # If it's already an array or processed, return as-is
    if hasattr(wind_speed_series, 'size'):
        return WindSpeedSeries(value=wind_speed_series, unit=SYMBOL_UNIT_WIND_SPEED)
    
    return wind_speed_series

def wind_speed_series_argument_callback(
    ctx: Context,
    wind_speed_series: WindSpeedSeries,
):
    """ """
    if isinstance(wind_speed_series, Path):
        return validate_path(wind_speed_series)

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

    if isinstance(wind_speed_series, int) and wind_speed_series == WIND_SPEED_DEFAULT:
        from pvgisprototype.core.arrays import create_array

        dtype = ctx.params.get("dtype", DATA_TYPE_DEFAULT)
        array_backend = ctx.params.get("array_backend", ARRAY_BACKEND_DEFAULT)
        shape_of_array = timestamps.shape  # Borrow shape from timestamps
        wind_speed_series = create_array(
            shape_of_array,
            dtype=dtype,
            init_method=WIND_SPEED_DEFAULT,
            backend=array_backend,
        )

    # at this point, wind_speed_series _should_ be an array !
    if wind_speed_series.size != len(timestamps):
        # Improve error message with useful hint/s ?
        raise ValueError(
            f"The number of wind_speed values ({wind_speed_series.size}) does not match the number of irradiance values ({len(timestamps)})."
        )

    return WindSpeedSeries(value=wind_speed_series, unit=SYMBOL_UNIT_WIND_SPEED)


def wind_speed_series_callback(
    ctx: Context,
    wind_speed_series: WindSpeedSeries,
):
    reference_series = ctx.params.get("timestamps", None)
    if wind_speed_series == WIND_SPEED_DEFAULT:
        from pvgisprototype.core.arrays import create_array

        dtype = ctx.params.get("dtype", DATA_TYPE_DEFAULT)
        array_backend = ctx.params.get("array_backend", ARRAY_BACKEND_DEFAULT)
        shape_of_array = reference_series.shape  # Borrow shape from timestamps
        wind_speed_series = create_array(
            shape_of_array,
            dtype=dtype,
            init_method=WIND_SPEED_DEFAULT,
            backend=array_backend,
        )

    if wind_speed_series.size != len(reference_series):
        raise ValueError(
            f"The number of wind_speed values ({wind_speed_series.size}) does not match the number of irradiance values ({len(reference_series)})."
        )
    return WindSpeedSeries(value=wind_speed_series, unit=SYMBOL_UNIT_WIND_SPEED)


wind_speed_typer_help = "Ambient wind_speed time series"

# typer_argument_wind_speed_time_series = typer.Argument(
#     help="Wind speed in meters per second.",
#     rich_help_panel=rich_help_panel_time_series,
# )

typer_argument_wind_speed_series = typer.Argument(
    help=wind_speed_typer_help,
    # min=WIND_SPEED_MINIMUM,
    # max=WIND_SPEED_MAXIMUM,
    rich_help_panel=rich_help_panel_meteorological_series,
    # is_eager=True,
    parser=parse_wind_speed_series,
    callback=wind_speed_series_argument_callback,
    show_default=False,
)
typer_option_wind_speed_series = typer.Option(
    help=wind_speed_typer_help,
    # min=WIND_SPEED_MINIMUM,
    # max=WIND_SPEED_MAXIMUM,
    rich_help_panel=rich_help_panel_meteorological_series,
    # is_eager=True,
    parser=parse_wind_speed_series,
    # callback=wind_speed_series_callback,
    callback=wind_speed_series_argument_callback,
)
typer_option_wind_speed_series_for_tmy = typer.Option(
    help=wind_speed_typer_help,
    # min=WIND_SPEED_MINIMUM,
    # max=WIND_SPEED_MAXIMUM,
    rich_help_panel=rich_help_panel_meteorological_series,
    # is_eager=True,
    parser=parse_wind_speed_series,
    callback=wind_speed_series_argument_callback,
)
