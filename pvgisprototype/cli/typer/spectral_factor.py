from pvgisprototype.log import logger
from pandas import to_numeric, DataFrame
from devtools import debug

# from pvgisprototype.api.spectrum.helpers import (

from pathlib import Path
from typing import Union
from pandas import read_csv
from pandas import Series

import numpy as np
import typer
from typer import Context

from pvgisprototype import SpectralFactorSeries
from pvgisprototype.api.datetime.datetimeindex import generate_datetime_series
# from pvgisprototype.api.spectrum.helpers import generate_banded_data
from pvgisprototype.api.spectrum.models import SpectralMismatchModel
from pvgisprototype.cli.rich_help_panel_names import (
    rich_help_panel_spectrum,
)
from pvgisprototype.cli.typer.path import validate_path
from pvgisprototype.constants import (
    DATA_TYPE_DEFAULT,
    RESPONSIVITY_SPECTRAL_DATA,
    SPECTRAL_FACTOR_DEFAULT,
    SPECTRAL_RESPONSIVITY_CSV_COLUMN_NAME_DEFAULT,
    UNITLESS,
    WAVELENGTHS_CSV_COLUMN_NAME_DEFAULT,
)


spectral_factor_typer_help = "Spectral factor time series"


def parse_spectral_factor_series(
    spectral_factor_input: Union[str, Path],
):
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


def spectral_factor_series_argument_callback(
    ctx: Context,
    spectral_factor_series: SpectralFactorSeries,
):
    """ """
    if isinstance(spectral_factor_series, Path):
        return validate_path(spectral_factor_series)

    from pvgisprototype.log import logger
    timestamps = ctx.params.get("timestamps", None)
    start_time = ctx.params.get("start_time")
    end_time = ctx.params.get("end_time")
    if timestamps is None and start_time is not None and end_time is not None:
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
            logger.error("Did you provide both a start and an end time ?")

    # How to use print(ctx.get_parameter_source('spectral_factor_series')) ?
    # See : class click.core.ParameterSource(value)

    if (
        isinstance(spectral_factor_series, int)
        and spectral_factor_series == SPECTRAL_FACTOR_DEFAULT
    ):
        dtype = ctx.params.get("dtype", DATA_TYPE_DEFAULT)
        if (
            timestamps is None
        ):  # This is to get photovoltaic_efficiency_time_series() going !
            from pandas import DatetimeIndex

            timestamps = DatetimeIndex([]) if timestamps is None else timestamps
            spectral_factor_series = np.full(12, SPECTRAL_FACTOR_DEFAULT, dtype=dtype)
        else:
            spectral_factor_series = np.full(
                len(timestamps), SPECTRAL_FACTOR_DEFAULT, dtype=dtype
            )

    # at this point, spectral_factor_series should be an array of size =12 or =timestamps !
    if spectral_factor_series is not None and not any(
        [
            spectral_factor_series.size == 12,
            spectral_factor_series.size == timestamps.size,
        ]
    ):
        message = f"The number of `spectral_factor` values ({spectral_factor_series.size}) is neither 12 (monthly values) nor does it match the number of timestamps ({timestamps.size})."
        logger.error(message)
        raise ValueError(message)

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
