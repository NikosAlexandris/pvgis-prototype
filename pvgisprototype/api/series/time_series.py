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
from pathlib import Path
from pvgisprototype.api.series.open import read_data_array_or_set
from pvgisprototype.api.series.temperature import get_temperature_series
from pvgisprototype.api.series.wind_speed import get_wind_speed_series
from pvgisprototype.api.series.spectral_factor import get_spectral_factor_series
from pvgisprototype.constants import (
    IN_MEMORY_FLAG_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)


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


def get_time_series_as_arrays_or_sets(
    dataset: dict,
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
) -> dict:
    """Open (lazy load) time series datasets from file paths into xarray DataArrays or Datasets.

    Opens multiple time series datasets by reading each file path provided in the
    input dictionary and returns them as a dictionary of opened (lazy loaded) xarray objects.

    Parameters
    ----------
    dataset : dict
        Dictionary mapping dataset names to file paths. Keys are dataset names,
        values are file paths to be opened (lazy loaded).
    mask_and_scale : bool, optional
        Whether to apply mask and scale transformations during opening,
        by default MASK_AND_SCALE_FLAG_DEFAULT
    in_memory : bool, optional
        Whether to open datasets entirely into memory or use lazy loading,
        by default IN_MEMORY_FLAG_DEFAULT
    verbose : int, optional
        Verbosity level for logging output during opening process,
        by default VERBOSE_LEVEL_DEFAULT

    Returns
    -------
    dict
        Dictionary mapping dataset names to opened (lazy loaded) xarray DataArrays or Datasets.
        Keys match the input dataset names, values are the opened xarray objects.

    """

    opened_dataset: dict = {}
    for name, path in dataset.items():
        if path is None:
            opened_dataset[name] = None
            continue
        opened_dataset[name] = read_data_array_or_set(
            input_data=path,
            mask_and_scale=mask_and_scale,
            in_memory=in_memory,
            verbose=verbose,
        )

    return opened_dataset
