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

from xarray import DataArray, Dataset
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    LOG_LEVEL_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    TEMPERATURE_DEFAULT,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
)
from numpy import array
from pandas import DatetimeIndex, Timestamp
from pvgisprototype import WindSpeedSeries


def get_wind_speed_series(
    longitude: float,
    latitude: float,
    timestamps: DatetimeIndex = str(Timestamp.now()),
    wind_speed_series: WindSpeedSeries | Path = array(TEMPERATURE_DEFAULT),
    neighbor_lookup: MethodForInexactMatches | None = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: float | None = TOLERANCE_DEFAULT,
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """ """
    if isinstance(wind_speed_series, Path):
        from pvgisprototype.api.series.select import select_time_series
        from pvgisprototype.api.utilities.conversions import (
            convert_float_to_degrees_if_requested,
        )
        from pvgisprototype.constants import DEGREES

        wind_speed_time_series = (
            select_time_series(
                time_series=wind_speed_series,
                longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
                latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
                timestamps=timestamps,
                # convert_longitude_360=convert_longitude_360,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                verbose=0,  # no verbosity here by choice!
                log=log,
            )
            .to_numpy()
            .astype(dtype=dtype)
        )

        if wind_speed_time_series.size == 1 and wind_speed_time_series.shape == ():
            wind_speed_time_series = array([wind_speed_time_series], dtype=dtype)
        return WindSpeedSeries(
            value=wind_speed_time_series,
            # unit=SYMBOL_UNIT_WIND_SPEED,
            data_source=wind_speed_series.name,
        )
    else:
        return wind_speed_series


def get_wind_speed_series_from_array_or_set(
    longitude: float,
    latitude: float,
    wind_speed_series: DataArray | Dataset,
    timestamps: DatetimeIndex = str(Timestamp.now()),
    neighbor_lookup: MethodForInexactMatches | None = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: float | None = TOLERANCE_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """Extract wind speed time series from xarray DataArray or Dataset.

    Selects and extracts wind speed data for a specific geographic location
    and time period from an xarray DataArray or Dataset. Performs spatial
    interpolation using the specified neighbor lookup method and temporal selection
    based on the provided timestamps. Returns a structured WindSpeedSeries
    object with proper units and metadata.

    Parameters
    ----------
    longitude : float
        Longitude coordinate for data extraction (in degrees or radians).
        Will be converted to degrees internally if needed.
    latitude : float
        Latitude coordinate for data extraction (in degrees or radians).
        Will be converted to degrees internally if needed.
    wind_speed_series : DataArray | Dataset
        Input xarray DataArray or Dataset containing wind speed data
        with spatial (longitude, latitude) and temporal dimensions.
    timestamps : DatetimeIndex, optional
        Time index for temporal selection of the data,
        by default str(Timestamp.now())
    neighbor_lookup : MethodForInexactMatches | None, optional
        Method for spatial interpolation when exact coordinate matches are not found,
        by default NEIGHBOR_LOOKUP_DEFAULT
    tolerance : float | None, optional
        Maximum distance tolerance for spatial interpolation,
        by default TOLERANCE_DEFAULT
    dtype : str, optional
        Data type for the output numpy array values,
        by default DATA_TYPE_DEFAULT
    log : int, optional
        Logging level for debug output,
        by default LOG_LEVEL_DEFAULT

    Returns
    -------
    WindSpeedSeries
        Structured wind speed time series object containing:
        - value: 1D numpy array with wind speed values
        - unit: Wind speed unit designation (typically m/s or km/h)
        - data_source: Original data source name from input

    Raises
    ------
    TypeError
        If wind_speed_series is not a DataArray or Dataset.

    Notes
    -----
    Wind speed data is typically measured at a standard height (often 10 or 2 meters) above
    ground level. The function automatically handles coordinate conversion to ensure
    compatibility with the underlying data. Scalar results are converted to 1D arrays
    for consistency in downstream processing.
    """
    from pvgisprototype.api.series.select import select_time_series_from_array_or_set

    if isinstance(wind_speed_series, DataArray | Dataset):
        from pvgisprototype.api.utilities.conversions import (
            convert_float_to_degrees_if_requested,
        )
        from pvgisprototype.constants import DEGREES

        wind_speed_time_series = (
            select_time_series_from_array_or_set(
                data=wind_speed_series,
                longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
                latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
                timestamps=timestamps,
                # convert_longitude_360=convert_longitude_360,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                verbose=0,  # no verbosity here by choice!
                log=log,
            )
            .to_numpy()
            .astype(dtype=dtype)
        )

        if wind_speed_time_series.size == 1 and wind_speed_time_series.shape == ():
            wind_speed_time_series = array([wind_speed_time_series], dtype=dtype)
    else:
        raise TypeError("Wind speed series must be a DataArray or Dataset.")

    return WindSpeedSeries(
        value=wind_speed_time_series,
        data_source=wind_speed_series.name,
    )
