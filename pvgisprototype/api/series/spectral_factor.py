from pathlib import Path

import numpy
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray, Dataset

from pvgisprototype import SpectralFactorSeries
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    LOG_LEVEL_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    SPECTRAL_FACTOR_DEFAULT,
    TOLERANCE_DEFAULT,
    UNITLESS,
    VERBOSE_LEVEL_DEFAULT,
)


def get_spectral_factor_series(
    longitude: float,
    latitude: float,
    timestamps: DatetimeIndex = str(Timestamp.now()),
    spectral_factor_series: SpectralFactorSeries | Path = numpy.array(
        SPECTRAL_FACTOR_DEFAULT
    ),
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
    if isinstance(spectral_factor_series, Path):

        from pvgisprototype.api.series.select import select_time_series
        from pvgisprototype.api.utilities.conversions import (
            convert_float_to_degrees_if_requested,
        )
        from pvgisprototype.constants import DEGREES

        return SpectralFactorSeries(
            value=select_time_series(
                time_series=spectral_factor_series,
                longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
                latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
                timestamps=timestamps,
                remap_to_month_start=False,
                # convert_longitude_360=convert_longitude_360,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                verbose=0,  # no verbosity here by choice!
                log=log,
            )
            .to_numpy()
            .astype(dtype=dtype),
            unit=UNITLESS,
            data_source=spectral_factor_series.name,
        )
    else:
        return spectral_factor_series


def get_spectral_factor_series_from_array_or_set(
    longitude: float,
    latitude: float,
    spectral_factor_series: DataArray | Dataset,
    timestamps: DatetimeIndex = str(Timestamp.now()),
    neighbor_lookup: MethodForInexactMatches | None = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: float | None = TOLERANCE_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """Extract spectral factor time series from xarray DataArray or Dataset.

    Selects and extracts spectral factor data for a specific geographic location
    and time period from an xarray DataArray or Dataset. Performs spatial
    interpolation using the specified neighbor lookup method and temporal selection
    based on the provided timestamps. Returns a structured SpectralFactorSeries
    object with proper units and metadata.

    Parameters
    ----------
    longitude : float
        Longitude coordinate for data extraction (in degrees or radians).
        Will be converted to degrees internally if needed.
    latitude : float
        Latitude coordinate for data extraction (in degrees or radians).
        Will be converted to degrees internally if needed.
    spectral_factor_series : DataArray | Dataset
        Input xarray DataArray or Dataset containing spectral factor data
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
    SpectralFactorSeries
        Structured spectral factor time series object containing:
        - value: 1D numpy array with spectral factor values
        - unit: Unitless designation (spectral factors are dimensionless)
        - data_source: Original data source name from input

    Raises
    ------
    TypeError
        If spectral_factor_series is not a DataArray or Dataset.
    """
    from pvgisprototype.api.series.select import select_time_series_from_array_or_set

    if isinstance(spectral_factor_series, DataArray | Dataset):
        from pvgisprototype.api.utilities.conversions import (
            convert_float_to_degrees_if_requested,
        )
        from pvgisprototype.constants import DEGREES

        spectral_factor_time_series = (
            select_time_series_from_array_or_set(
                data=spectral_factor_series,
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

        if (
            spectral_factor_time_series.size == 1
            and spectral_factor_time_series.shape == ()
        ):
            spectral_factor_time_series = numpy.array(
                [spectral_factor_time_series], dtype=dtype
            )
    else:
        raise TypeError("Spectral factor series must be a DataArray or Dataset.")

    return SpectralFactorSeries(
        value=spectral_factor_time_series,
        unit=UNITLESS,
        data_source=spectral_factor_series.name,
    )
