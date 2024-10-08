from pandas import NaT, Timestamp
from pvgisprototype.log import logger

from pathlib import Path

import numpy as np
import typer
from typer import Context

from pvgisprototype import SpectralFactorSeries
from pvgisprototype.api.datetime.datetimeindex import generate_datetime_series
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_spectrum,
)
from pvgisprototype.cli.typer.path import validate_path
from pvgisprototype.constants import (
    DATA_TYPE_DEFAULT,
    SPECTRAL_FACTOR_DEFAULT,
    UNITLESS,
)

from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_spectral_factor,
)
import typer


spectral_factor_model_typer_help = "Spectral factor model"
typer_option_spectral_factor_model = typer.Option(
    help=spectral_factor_model_typer_help,
    is_eager=True,
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_spectral_factor,
)



def parse_spectral_factor_series(
    spectral_factor_input: str | Path | None,
) -> str | Path | None:
    """
    Notes
    -----
    FIXME: Re-design ?

    """
    try:
        if (
            isinstance(spectral_factor_input, (str, Path))
            and Path(spectral_factor_input).exists()
        ):
            return Path(spectral_factor_input)

        # -------------------------------------------------------------- FIXME
        # Further develop the logic here :
        #   either 12 monthly values  or  a full time series ?

        if isinstance(spectral_factor_input, str):
            from numpy import fromstring
            spectral_factor_input = fromstring(spectral_factor_input, sep=",")
        # --------------------------------------------------------------------

        return spectral_factor_input

    except ValueError as e:  # conversion to float failed
        print(f"Error parsing input: {e}")
        return None


from pandas import Timestamp, NaT
import numpy as np

# Helper function to generate timestamps
def _generate_timestamps_if_missing(start_time, end_time, ctx, logger):
    """Generate timestamps if both start_time and end_time are provided or return current UTC time."""
    if start_time is NaT and end_time is NaT:
        return Timestamp.now(tz='UTC')

    if start_time is not NaT and end_time is not NaT:
        periods = ctx.params.get("periods", None)
        from pvgisprototype.constants import TIMESTAMPS_FREQUENCY_DEFAULT
        
        frequency = ctx.params.get("frequency", TIMESTAMPS_FREQUENCY_DEFAULT) if not periods else None
        return generate_datetime_series(
            start_time=start_time,
            end_time=end_time,
            periods=periods,
            frequency=frequency,
            timezone=ctx.params.get("timezone"),
            name=ctx.params.get("datetimeindex_name", None),
        )
    
    logger.error("Both start_time and end_time must be provided for timestamp generation.")
    return None


def _initialize_spectral_factor_series(timestamps, dtype):
    """Initialize the spectral factor series based on the size of timestamps or default size."""
    if isinstance(timestamps, Timestamp):
        return np.full(1, SPECTRAL_FACTOR_DEFAULT, dtype=dtype)
    return np.full(timestamps.size, SPECTRAL_FACTOR_DEFAULT, dtype=dtype)


def _validate_spectral_factor_size(spectral_factor_series, timestamps, logger):
    """Validate that the size of spectral_factor_series matches either 12 (months) or timestamps size."""

    # If timestamps is a single Timestamp
    if isinstance(timestamps, Timestamp):
        expected_size = 1
    else:
        expected_size = timestamps.size

    # Validate the size of the spectral_factor_series
    if spectral_factor_series.size not in [12, expected_size]:
        message = (
            f"The number of `spectral_factor` values ({spectral_factor_series.size}) is neither 12 "
            f"(monthly values) nor does it match the number of timestamps ({expected_size})."
        )
        logger.error(message)
        raise ValueError(message)


def spectral_factor_series_argument_callback(
    ctx: Context,
    spectral_factor_series: SpectralFactorSeries,
):
    """Callback function to process spectral factor series argument."""
    
    if isinstance(spectral_factor_series, Path):
        return validate_path(spectral_factor_series)

    from pvgisprototype.log import logger

    # retrieve parameters from context
    timestamps = ctx.params.get("timestamps", None)
    start_time = ctx.params.get("start_time", NaT)
    end_time = ctx.params.get("end_time", NaT)
    dtype = ctx.params.get("dtype", DATA_TYPE_DEFAULT)

    # if timestamps missing or NaT
    if timestamps is None or timestamps is NaT:
        timestamps = _generate_timestamps_if_missing(start_time, end_time, ctx, logger)

    # default spectral factor case
    if isinstance(spectral_factor_series, int) and spectral_factor_series == SPECTRAL_FACTOR_DEFAULT:
        spectral_factor_series = _initialize_spectral_factor_series(timestamps, dtype)
    
    # validate spectral_factor_series size
    if spectral_factor_series is not None:
        _validate_spectral_factor_size(spectral_factor_series, timestamps, logger)

    return SpectralFactorSeries(value=spectral_factor_series, unit=UNITLESS)


def spectral_factor_series_option_callback(
    ctx: Context,
    spectral_factor_series: SpectralFactorSeries,
):
    """ """
    if spectral_factor_series is None:
        return np.ndarray([])

    reference_series = ctx.params.get("irradiance_series")
    from pvgisprototype.log import logger

    if spectral_factor_series is not None and any(
        spectral_factor_series.size
        != 12 | spectral_factor_series.size
        != len(reference_series)
    ):
        message = f"The number of `spectral_factor` values ({spectral_factor_series.size}) is neither 12 (monthly values) nor does it match the number of irradiance values ({reference_series.size})."
        logger.error(message)
        raise ValueError(message)

    return SpectralFactorSeries(value=spectral_factor_series, unit=UNITLESS)


spectral_factor_typer_help = "Spectral factor time series"
typer_argument_spectral_factor_series = typer.Option(
    help=spectral_factor_typer_help,
    rich_help_panel=rich_help_panel_spectrum,
    # is_eager=True,
    parser=parse_spectral_factor_series,
    callback=spectral_factor_series_argument_callback,
    show_default=False,
)
typer_option_spectral_factor_series = typer.Option(
    help=spectral_factor_typer_help,
    rich_help_panel=rich_help_panel_spectrum,
    is_eager=True,
    parser=parse_spectral_factor_series,
    callback=spectral_factor_series_option_callback,
)
