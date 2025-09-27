import numpy as np

from pvgisprototype import (
    SpectralFactorSeries,
)
from pvgisprototype.constants import (
    SPECTRAL_FACTOR_DEFAULT,
)

async def create_spectral_factor_series(
    spectral_factor_series: float | None = None,
) -> SpectralFactorSeries:
    """ """
    if isinstance(spectral_factor_series, float):
        return SpectralFactorSeries(
            value=np.array(spectral_factor_series, dtype=np.float32)
        )

    return SpectralFactorSeries(
        value=np.array(SPECTRAL_FACTOR_DEFAULT, dtype=np.float32)
    )
