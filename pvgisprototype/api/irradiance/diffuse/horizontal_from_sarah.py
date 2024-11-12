from pathlib import Path
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Irradiance
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIFFUSE_HORIZONTAL_IRRADIANCE,
    DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIRECT_HORIZONTAL_IRRADIANCE_SOURCE_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    GLOBAL_HORIZONTAL_IRRADIANCE_SOURCE_COLUMN_NAME,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_SOURCE_COLUMN_NAME,
    IRRADIANCE_UNIT,
    LOG_LEVEL_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    RADIATION_MODEL_COLUMN_NAME,
    TITLE_KEY_NAME,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.core.hashing import generate_hash

# def safe_select_time_series(*args, **kwargs):
#     try:
#         # Your existing select_time_series function call
#         return select_time_series(*args, **kwargs).to_numpy().astype(dtype=kwargs.get('dtype'))
#     except Exception as e:
#         # Handle or log the exception as needed
#         print(f"Error during task execution: {e}")
#         return None


# def read_horizontal_irradiance_components_from_sarah(...):
#     if multi_thread:
#         with ThreadPoolExecutor(max_workers=2) as executor:
#             futures = {
#                 executor.submit(safe_select_time_series, time_series=shortwave, longitude=longitude, latitude=latitude, timestamps=timestamps, mask_and_scale=mask_and_scale, neighbor_lookup=neighbor_lookup, tolerance=tolerance, in_memory=in_memory, log=log, dtype=dtype): "global",
#                 executor.submit(safe_select_time_series, time_series=direct, longitude=longitude, latitude=latitude, timestamps=timestamps, mask_and_scale=mask_and_scale, neighbor_lookup=neighbor_lookup, tolerance=tolerance, in_memory=in_memory, log=log, dtype=dtype): "direct"
#             }
#             from concurrent.futures import as_completed
#             for future in as_completed(futures):
#                 try:
#                     result = future.result()
#                     if futures[future] == "global":
#                         global_horizontal_irradiance_series = result
#                     else:
#                         direct_horizontal_irradiance_series = result
#                 except Exception as e:
#                     # Handle or log the exception
#                     print(f"Error retrieving task result: {e}")


@log_function_call
def read_horizontal_irradiance_components_from_sarah(
    shortwave: Path,
    direct: Path,
    longitude: float,
    latitude: float,
    timestamps: DatetimeIndex = None,
    neighbor_lookup: MethodForInexactMatches = None,
    tolerance: float | None = TOLERANCE_DEFAULT,
    mask_and_scale: bool = False,
    in_memory: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
):
    """Read horizontal irradiance components from SARAH time series.

    Read the global and direct horizontal irradiance components incident on a
    solar surface from SARAH time series.

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
    if multi_thread:
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_global_horizontal_irradiance_series = executor.submit(
                select_time_series,
                time_series=shortwave,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                log=log,
            )
            future_direct_horizontal_irradiance_series = executor.submit(
                select_time_series,
                time_series=direct,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                log=log,
            )
            global_horizontal_irradiance_series = (
                future_global_horizontal_irradiance_series.result()
                .to_numpy()
                .astype(dtype=dtype)
            )
            direct_horizontal_irradiance_series = (
                future_direct_horizontal_irradiance_series.result()
                .to_numpy()
                .astype(dtype=dtype)
            )
    else:
        global_horizontal_irradiance_series = (
            select_time_series(
                time_series=shortwave,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                verbose=verbose,
                log=log,
            )
            .to_numpy()
            .astype(dtype=dtype)
        )
        direct_horizontal_irradiance_series = (
            select_time_series(
                time_series=direct,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                verbose=verbose,
                log=log,
            )
            .to_numpy()
            .astype(dtype=dtype)
        )

    horizontal_irradiance_components = {
        GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: global_horizontal_irradiance_series,
        DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
        IRRADIANCE_SOURCE_COLUMN_NAME: 'External time series',
        GLOBAL_HORIZONTAL_IRRADIANCE_SOURCE_COLUMN_NAME: f'{shortwave}',
        DIRECT_HORIZONTAL_IRRADIANCE_SOURCE_COLUMN_NAME: f'{direct}',
    }

    return horizontal_irradiance_components


@log_function_call
def calculate_diffuse_horizontal_component_from_sarah(
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

    components_container = {
        "Diffuse irradiance": lambda: (
            {
                TITLE_KEY_NAME: DIFFUSE_HORIZONTAL_IRRADIANCE,
                DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series,
            }
            if verbose > 1
            else {}
        ),
        "Time series": lambda: {
            TITLE_KEY_NAME: DIFFUSE_HORIZONTAL_IRRADIANCE
            + " & other horizontal components",
            GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: global_horizontal_irradiance_series,  # .to_numpy(),
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,  # .to_numpy(),
            IRRADIANCE_SOURCE_COLUMN_NAME: "External time series",
        },
        "Sources": lambda: (
            {
                IRRADIANCE_SOURCE_COLUMN_NAME: "External time series",
            }
            if verbose > 1
            else {}
        ),
        "fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    diffuse_horizontal_irradiance_series
                ),
            }
            if fingerprint
            else {}
        ),
    }

    components = {}
    for _, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=diffuse_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
        value=diffuse_horizontal_irradiance_series,
        unit=IRRADIANCE_UNIT,
        position_algorithm="",
        timing_algorithm="",
        elevation=None,
        surface_orientation=None,
        surface_tilt=None,
        components=components,
    )
