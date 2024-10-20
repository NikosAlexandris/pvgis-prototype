from pathlib import Path
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
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
)
import numpy
from pandas import DatetimeIndex, Timestamp
from pvgisprototype import SpectralFactorSeries


def get_spectral_factor_series(
    longitude: float,
    latitude: float,
    timestamps: DatetimeIndex = str(Timestamp.now()),
    spectral_factor_series: SpectralFactorSeries | Path = numpy.array(SPECTRAL_FACTOR_DEFAULT),
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
        from pvgisprototype.constants import DEGREES
        from pvgisprototype.api.utilities.conversions import (
            convert_float_to_degrees_if_requested,
        )

        return SpectralFactorSeries(
            value=select_time_series(
                time_series=spectral_factor_series,
                longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
                latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
                timestamps=timestamps,
                remap_to_month_start=True,
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
