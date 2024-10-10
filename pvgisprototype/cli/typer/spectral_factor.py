from pandas import NaT, Timestamp
from pvgisprototype.log import logger

from pathlib import Path

from numpy import ndarray, fromstring
from numpy import full as numpy_full
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
    ) -> Path | ndarray | None:
    """
    Parses the spectral factor input, which can be a file path or a comma-separated string.

    Parameters
    ----------
    spectral_factor_input : str or Path
        The input representing either a file path or a string of spectral factors.

    Returns
    -------
    Path or np.ndarray or None
        Returns a Path object if the input is a valid file path,
        or a NumPy array if the input is a valid string of spectral factors.
        Returns None if the input cannot be parsed.
    """
    try:
        if isinstance(spectral_factor_input, (str, Path)):
            path = Path(spectral_factor_input)
            if path.exists():
                return path

        if isinstance(spectral_factor_input, str):
            spectral_factor_array = fromstring(spectral_factor_input, sep=",")
            if spectral_factor_array.size > 0:
                return spectral_factor_array
            else:
                raise ValueError("The input string could not be parsed into valid spectral factors.")

    except ValueError as e:
        # Handle parsing error
        print(f"Error parsing input: {e}")
        return None


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
        return numpy_full(1, SPECTRAL_FACTOR_DEFAULT, dtype=dtype)
    return numpy_full(timestamps.size, SPECTRAL_FACTOR_DEFAULT, dtype=dtype)


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
    spectral_factor_series: Path | ndarray | None,
) -> SpectralFactorSeries:
    """Callback function to process spectral factor series argument."""
    if spectral_factor_series is None:
        spectral_factor_series = SPECTRAL_FACTOR_DEFAULT
    
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
    spectral_factor_series: Path | ndarray | None,
) -> SpectralFactorSeries:
    """
    Callback function to validate the spectral factor series option.

    Parameters
    ----------
    ctx : Context
        The Typer or Click context, providing access to other parameters like `irradiance_series`.
    spectral_factor_series : Path | ndarray | None
        The spectral factor series, either as a file path or a NumPy array.
    
    Returns
    -------
    SpectralFactorSeries
        The validated spectral factor series, either containing 12 monthly values or matching
        the length of the irradiance time series.
    
    Raises
    ------
    ValueError
        If the size of the spectral factor series is neither 12 nor the same as the irradiance series.
    """
    if spectral_factor_series is None:
        return SpectralFactorSeries(value=ndarray([]), unit=UNITLESS)

    if isinstance(spectral_factor_series, ndarray):
        reference_series = ctx.params.get("irradiance_series")
        if reference_series is None:
            raise ValueError("Irradiance series not found in context.")

        if spectral_factor_series.size != 12 and spectral_factor_series.size != len(reference_series):
            from pvgisprototype.log import logger
            message = (
                f"The number of `spectral_factor` values ({spectral_factor_series.size}) is neither 12 "
                f"(monthly values) nor does it match the number of irradiance values ({len(reference_series)})."
            )
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
