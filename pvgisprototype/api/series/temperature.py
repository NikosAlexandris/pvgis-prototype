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
from pvgisprototype import TemperatureSeries


def get_temperature_series_from_array_or_set(
    longitude: float,
    latitude: float,
    temperature_series: DataArray | Dataset,
    timestamps: DatetimeIndex = str(Timestamp.now()),
    neighbor_lookup: MethodForInexactMatches | None = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: float | None = TOLERANCE_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """Extract temperature time series from xarray DataArray or Dataset.

    Selects and extracts temperature data for a specific geographic location
    and time period from an xarray DataArray or Dataset. Performs spatial
    interpolation using the specified neighbor lookup method and temporal selection
    based on the provided timestamps. Returns a structured TemperatureSeries
    object with proper units and metadata.

    Parameters
    ----------
    longitude : float
        Longitude coordinate for data extraction (in degrees or radians).
        Will be converted to degrees internally if needed.
    latitude : float
        Latitude coordinate for data extraction (in degrees or radians).
        Will be converted to degrees internally if needed.
    temperature_series : DataArray | Dataset
        Input xarray DataArray or Dataset containing temperature data
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
    TemperatureSeries
        Structured temperature time series object containing:
        - value: 1D numpy array with temperature values
        - unit: Temperature unit designation (typically Celsius or Kelvin)
        - data_source: Original data source name from input

    Raises
    ------
    TypeError
        If temperature_series is not a DataArray or Dataset.

    Notes
    -----
    The function automatically handles coordinate conversion to ensure compatibility
    with the underlying data. Scalar results are converted to 1D arrays for
    consistency in downstream processing. Temperature units are preserved from
    the original dataset metadata.
    """
    from pvgisprototype.api.series.select import select_time_series_from_array_or_set

    if isinstance(temperature_series, DataArray | Dataset):
        from pvgisprototype.api.utilities.conversions import (
            convert_float_to_degrees_if_requested,
        )
        from pvgisprototype.constants import DEGREES

        temperature_times_series = (
            select_time_series_from_array_or_set(
                data=temperature_series,
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

        if temperature_times_series.size == 1 and temperature_times_series.shape == ():
            temperature_times_series = array([temperature_times_series], dtype=dtype)
    else:
        raise TypeError("Temperature series must be a DataArray or Dataset.")

    return TemperatureSeries(
        value=temperature_times_series,
        data_source=temperature_series.name,
    )
