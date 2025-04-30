from pathlib import Path
import numpy
from pandas import DatetimeIndex, Timestamp

from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    LOG_LEVEL_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_function_call, logger


@log_function_call
def read_horizontal_irradiance_components_from_sarah(
    shortwave: Path | None,
    direct: Path | None,
    longitude: float,
    latitude: float,
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    neighbor_lookup: MethodForInexactMatches = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: float | None = TOLERANCE_DEFAULT,
    mask_and_scale: bool = False,
    in_memory: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
) -> tuple[numpy.ndarray, numpy.ndarray]:
    """Read horizontal irradiance components from SARAH time series.

    Read the global and direct horizontal irradiance components incident on a
    solar surface from SARAH time series.

    Parameters
    ----------
    shortwave: Path
        Filename of surface short-wave (solar) radiation downwards time series
        (short name : `ssrd`) from ECMWF which is the solar radiation that
        reaches a horizontal plane at the surface of the Earth. This parameter
        comprises both direct and diffuse solar radiation.

    Returns
    -------
    tuple(GlobalHorizontalIrradiance, DirectHorizontalIrradiance)

    """
    if verbose > 0:
        logger.info(
            ":information: Reading the global and direct horizontal irradiance components from external data ...",
            alt=f":information: [black on white][bold]Reading[/bold] the [orange]global[/orange] and [yellow]direct[/yellow] horizontal irradiance components [bold]from external data[/bold] ...[/black on white]",
        )
    if multi_thread:
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_global_horizontal_irradiance_series = executor.submit(
                select_time_series,
                time_series=shortwave,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                verbose=0,
                log=log,
            )
            future_direct_horizontal_irradiance_series = executor.submit(
                select_time_series,
                time_series=direct,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                verbose=0,
                log=log,
            )
            global_horizontal_irradiance_series = (
                future_global_horizontal_irradiance_series.result()
                .to_numpy()
                .astype(dtype=dtype)
            )
            direct_horizontal_irradiance_series = (
                future_direct_horizontal_irradiance_series.result()
                .to_numpy()
                .astype(dtype=dtype)
            )
    else:
        global_horizontal_irradiance_series = (
            select_time_series(
                time_series=shortwave,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                verbose=verbose,
                log=log,
            )
            .to_numpy()
            .astype(dtype=dtype)
        )
        direct_horizontal_irradiance_series = (
            select_time_series(
                time_series=direct,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                verbose=verbose,
                log=log,
            )
            .to_numpy()
            .astype(dtype=dtype)
        )

    return global_horizontal_irradiance_series, direct_horizontal_irradiance_series
