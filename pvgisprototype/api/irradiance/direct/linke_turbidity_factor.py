from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import LINKE_TURBIDITY_UNIT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from numpy import array as numpy_array
from devtools import debug


@log_function_call
def correct_linke_turbidity_factor_series(
    linke_turbidity_factor_series: LinkeTurbidityFactor,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
) -> LinkeTurbidityFactor:
    """Calculate the air mass 2 Linke turbidity factor.

    Calculate the air mass 2 Linke atmospheric turbidity factor for a time series.

    Parameters
    ----------
    linke_turbidity_factor_series: (List[LinkeTurbidityFactor] or LinkeTurbidityFactor)
        The Linke turbidity factors as a list of LinkeTurbidityFactor objects
        or a single object.

    Returns
    -------
    List[LinkeTurbidityFactor] or LinkeTurbidityFactor
        The corrected Linke turbidity factors as a list of LinkeTurbidityFactor
        objects or a single object.

    """
    corrected_linke_turbidity_factors = -0.8662 * numpy_array(linke_turbidity_factor_series.value, dtype=dtype)

    log_data_fingerprint(
        data=corrected_linke_turbidity_factors,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    return LinkeTurbidityFactor(
        value=corrected_linke_turbidity_factors,
        unit=LINKE_TURBIDITY_UNIT,
    )
