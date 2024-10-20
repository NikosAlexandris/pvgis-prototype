from pathlib import Path
import asyncio

from numpy import spacing
from pvgisprototype.api.series.temperature import get_temperature_series
from pvgisprototype.api.series.wind_speed import get_wind_speed_series
from pvgisprototype.api.series.spectral_factor import get_spectral_factor_series


def get_time_series(
    temperature_series: Path,
    wind_speed_series: Path,
    spectral_factor_series: Path,
    longitude,
    latitude,
    timestamps,
    neighbor_lookup,
    tolerance,
    mask_and_scale,
    in_memory,
    dtype,
    array_backend,
    multi_thread,
    verbose,
    log,
):
    if isinstance(temperature_series, Path):
        temperature_series = get_temperature_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                temperature_series=temperature_series,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                dtype=dtype,
                array_backend=array_backend,
                multi_thread=multi_thread,
                verbose=verbose,
                log=log,
            )
    if isinstance(wind_speed_series, Path):
        wind_speed_series = get_wind_speed_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                wind_speed_series=wind_speed_series,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                dtype=dtype,
                array_backend=array_backend,
                multi_thread=multi_thread,
                verbose=verbose,
                log=log,
            )
    if isinstance(spectral_factor_series, Path):
        spectral_factor_series = get_spectral_factor_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                spectral_factor_series=spectral_factor_series,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                dtype=dtype,
                array_backend=array_backend,
                multi_thread=multi_thread,
                verbose=verbose,
                log=log,
            )

    return temperature_series, wind_speed_series, spectral_factor_series

