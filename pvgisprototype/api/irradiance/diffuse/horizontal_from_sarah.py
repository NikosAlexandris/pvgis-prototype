from pvgisprototype.log import logger
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from pandas import DatetimeIndex
from pathlib import Path
from typing import Optional
from typing import List
from rich import print
import numpy as np
from math import cos, sin, pi
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype import Irradiance
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_INCIDENCE_ALGORITHM_DEFAULT
from pvgisprototype.api.position.altitude_series import model_solar_altitude_time_series
from pvgisprototype.api.position.incidence_series import model_solar_incidence_time_series
from pvgisprototype.api.position.azimuth_series import model_solar_azimuth_time_series
from pvgisprototype.api.irradiance.direct.horizontal import calculate_direct_horizontal_irradiance_time_series
from pvgisprototype.api.irradiance.extraterrestrial import calculate_extraterrestrial_normal_irradiance_time_series
from pvgisprototype.api.irradiance.limits import LOWER_PHYSICALLY_POSSIBLE_LIMIT
from pvgisprototype.api.irradiance.limits import UPPER_PHYSICALLY_POSSIBLE_LIMIT
from pvgisprototype.api.irradiance.loss import calculate_angular_loss_factor_for_nondirect_irradiance
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_series_to_degrees_arrays_if_requested
from pvgisprototype.validation.hashing import generate_hash
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_COLUMN_NAME
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import TERM_N_IN_SHADE
from pvgisprototype.constants import LINKE_TURBIDITY_UNIT
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import DEGREES
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.constants import ANGLE_UNITS_COLUMN_NAME
from pvgisprototype.constants import TITLE_KEY_NAME
from pvgisprototype.constants import LOSS_COLUMN_NAME
from pvgisprototype.constants import SURFACE_TILT_COLUMN_NAME
from pvgisprototype.constants import AZIMUTH_COLUMN_NAME
from pvgisprototype.constants import ALTITUDE_COLUMN_NAME
from pvgisprototype.constants import GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE_BEFORE_LOSS_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_HORIZONTAL_IRRADIANCE
from pvgisprototype.constants import DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_CLEAR_SKY_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import LINKE_TURBIDITY_COLUMN_NAME
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import ANGULAR_LOSS_FACTOR_FLAG_DEFAULT
from pvgisprototype.constants import INCIDENCE_COLUMN_NAME
from pvgisprototype.constants import INCIDENCE_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import OUT_OF_RANGE_INDICES_COLUMN_NAME
from pvgisprototype.constants import TERM_N_COLUMN_NAME
from pvgisprototype.constants import KB_RATIO_COLUMN_NAME
from pvgisprototype.constants import AZIMUTH_DIFFERENCE_COLUMN_NAME
from pvgisprototype.constants import RADIATION_MODEL_COLUMN_NAME
from pvgisprototype.constants import HOFIERKA_2002
from pvgisprototype.constants import RANDOM_TIMESTAMPS_FLAG_DEFAULT
from pvgisprototype.constants import MINUTES
from pvgisprototype.constants import MULTI_THREAD_FLAG_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT
from pvgisprototype.constants import NEIGHBOR_LOOKUP_DEFAULT
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT


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
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    mask_and_scale: bool = False,
    in_memory: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
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
                mask_and_scale=mask_and_scale,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                in_memory=in_memory,
                log=log,
            )
            future_direct_horizontal_irradiance_series = executor.submit(
                select_time_series,
                time_series=direct,
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                mask_and_scale=mask_and_scale,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                in_memory=in_memory,
                log=log,
            )
            global_horizontal_irradiance_series = (
                future_global_horizontal_irradiance_series.result().to_numpy().astype(dtype=dtype)
            )
            direct_horizontal_irradiance_series = (
                future_direct_horizontal_irradiance_series.result().to_numpy().astype(dtype=dtype)
            )
    else:
        global_horizontal_irradiance_series = select_time_series(
            time_series=shortwave,
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            mask_and_scale=mask_and_scale,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            in_memory=in_memory,
            log=log,
        ).to_numpy().astype(dtype=dtype)
        direct_horizontal_irradiance_series = select_time_series(
            time_series=direct,
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            mask_and_scale=mask_and_scale,
            neighbor_lookup=neighbor_lookup,
            tolerance=tolerance,
            in_memory=in_memory,
            log=log,
        ).to_numpy().astype(dtype=dtype)

    horizontal_irradiance_components = {
        GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: global_horizontal_irradiance_series,
        DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
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
            + f" matches the single value "
            + f"{single_value}"
        )
        logger.warning(warning)

    components_container = {
        'main': lambda: {
            TITLE_KEY_NAME: DIFFUSE_HORIZONTAL_IRRADIANCE,
            DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series,
        },
        
        'extended': lambda: {
            TITLE_KEY_NAME: DIFFUSE_HORIZONTAL_IRRADIANCE + " & other horizontal components",
            GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: global_horizontal_irradiance_series,#.to_numpy(),
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,#.to_numpy(),
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        } if verbose > 1 else {},

        'fingerprint': lambda: {
            FINGERPRINT_COLUMN_NAME: generate_hash(diffuse_horizontal_irradiance_series),
        } if fingerprint else {},
    }

    components = {}
    for key, component in components_container.items():
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
            unit=IRRADIANCE_UNITS,
            position_algorithm="",
            timing_algorithm="",
            elevation=None,
            surface_orientation=None,
            surface_tilt=None,
            components=components,
            )
