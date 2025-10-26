from pathlib import Path

from numpy import array
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray, Dataset

from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.series.select import select_time_series_from_array_or_set
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    IN_MEMORY_FLAG_DEFAULT,
    LOG_LEVEL_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)


def get_direct_horizontal_irradiance_series(
    longitude: float,
    latitude: float,
    timestamps: DatetimeIndex = str(Timestamp.now()),
    direct_horizontal_irradiance_series: Path | None = None,
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
    if isinstance(direct_horizontal_irradiance_series, Path):
        from pvgisprototype.api.series.select import select_time_series
        from pvgisprototype.api.utilities.conversions import (
            convert_float_to_degrees_if_requested,
        )
        from pvgisprototype.constants import DEGREES

        direct_horizontal_irradiance_series = (
            select_time_series(
                time_series=direct_horizontal_irradiance_series,
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

        if direct_horizontal_irradiance_series.size == 1 and direct_horizontal_irradiance_series.shape == ():  # type: ignore[union-attr]
            direct_horizontal_irradiance_series = array(  # type: ignore[assignment]
                [direct_horizontal_irradiance_series], dtype=dtype
            )
    return direct_horizontal_irradiance_series


def get_direct_horizontal_irradiance_series_from_array_or_set(
    longitude: float,
    latitude: float,
    direct_horizontal_irradiance_series: DataArray | Dataset,
    timestamps: DatetimeIndex = str(Timestamp.now()),
    neighbor_lookup: MethodForInexactMatches | None = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: float | None = TOLERANCE_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """Extract direct horizontal irradiance time series from xarray DataArray or Dataset.

    Selects and extracts direct horizontal irradiance data for a specific geographic
    location and time period from an xarray DataArray or Dataset. Performs spatial
    interpolation using the specified neighbor lookup method and temporal selection
    based on the provided timestamps.

    Parameters
    ----------
    longitude : float
        Longitude coordinate for data extraction (in degrees or radians).
        Will be converted to degrees internally if needed.
    latitude : float
        Latitude coordinate for data extraction (in degrees or radians).
        Will be converted to degrees internally if needed.
    direct_horizontal_irradiance_series : DataArray | Dataset
        Input xarray DataArray or Dataset containing direct horizontal irradiance data
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
        Data type for the output numpy array,
        by default DATA_TYPE_DEFAULT
    log : int, optional
        Logging level for debug output,
        by default LOG_LEVEL_DEFAULT

    Returns
    -------
    numpy.ndarray
        Direct horizontal irradiance time series as a 1D numpy array with the
        specified dtype. Single scalar values are automatically converted to
        1D arrays with one element.

    Raises
    ------
    TypeError
        If direct_horizontal_irradiance_series is not a DataArray or Dataset.

    Notes
    -----
    The function automatically handles coordinate conversion to ensure compatibility
    with the underlying data. Scalar results are converted to 1D arrays for
    consistency in downstream processing.
    """
    if isinstance(direct_horizontal_irradiance_series, DataArray | Dataset):
        from pvgisprototype.api.utilities.conversions import (
            convert_float_to_degrees_if_requested,
        )
        from pvgisprototype.constants import DEGREES

        direct_horizontal_irradiance_time_series = (
            select_time_series_from_array_or_set(
                data=direct_horizontal_irradiance_series,
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
            direct_horizontal_irradiance_time_series.size == 1
            and direct_horizontal_irradiance_time_series.shape == ()
        ):
            direct_horizontal_irradiance_time_series = array(
                [direct_horizontal_irradiance_time_series], dtype=dtype
            )
    else:
        raise TypeError(
            "Direct horizontal irradiance series must be a DataArray or Dataset."
        )

    return direct_horizontal_irradiance_time_series
