from devtools import debug
import numpy

from pvgisprototype import (
    DiffuseSkyReflectedHorizontalIrradianceFromExternalData,
)
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.arrays import create_array
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
def calculate_diffuse_horizontal_irradiance_from_external_data(
    global_horizontal_irradiance_series,
    direct_horizontal_irradiance_series,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,  # Not yet integrated !
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
):
    """Calculate the diffuse horizontal irradiance from SARAH time series.

    Calculate the diffuse horizontal irradiance incident on a solar surface
    from SARAH time series.

    Parameters
    ----------
    shortwave: Path
        Filename of surface short-wave (solar) radiation downwards time series
        (short name : `ssrd`) from ECMWF which is the solar radiation that
        reaches a horizontal plane at the surface of the Earth. This parameter
        comprises both direct and diffuse solar radiation.

    Returns
    -------
    diffuse_irradiance: float
        The diffuse radiant flux incident on a surface per unit area in W/m².
    """
    diffuse_horizontal_irradiance_series = (
        global_horizontal_irradiance_series - direct_horizontal_irradiance_series
    ).astype(dtype=dtype)

    if diffuse_horizontal_irradiance_series.size == 1:
        single_value = float(diffuse_horizontal_irradiance_series)
        warning = (
            f"{exclamation_mark} The selected timestamp "
            + " matches the single value "
            + f"{single_value}"
        )
        logger.warning(warning)

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=diffuse_horizontal_irradiance_series,
        # shape=timestamps.shape,
        shape=global_horizontal_irradiance_series.shape,
        data_model=DiffuseSkyReflectedHorizontalIrradianceFromExternalData(),
    )

    diffuse_horizontal_irradiance_series = DiffuseSkyReflectedHorizontalIrradianceFromExternalData(
        value=diffuse_horizontal_irradiance_series,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        global_horizontal_irradiance=global_horizontal_irradiance_series,
        direct_horizontal_irradiance=direct_horizontal_irradiance_series,
    )
    diffuse_horizontal_irradiance_series.build_output(
        verbose=verbose, fingerprint=fingerprint
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=diffuse_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )


    return diffuse_horizontal_irradiance_series
