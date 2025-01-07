"""
This Python module is part of PVGIS' API. It implements functions to calculate
the direct normal solar irradiance.

_Direct_ or _beam_ irradiance is one of the main components of solar
irradiance. It comes perpendicular from the Sun and is not scattered before it
irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _direct_ irradiance.
"""

from zoneinfo import ZoneInfo

from devtools import debug
from numpy import ndarray
from pandas import DatetimeIndex

from pvgisprototype import (
    Irradiance,
    Latitude,
    Longitude,
)
from pvgisprototype.algorithms.pvis.direct.normal_from_horizontal import (
    calculate_direct_normal_from_horizontal_irradiance_series_pvgis,
)
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_radians_if_requested,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ALTITUDE_COLUMN_NAME,
    ANGLE_UNITS_COLUMN_NAME,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIRECT_NORMAL_IRRADIANCE,
    DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    PERIGEE_OFFSET,
    PERIGEE_OFFSET_COLUMN_NAME,
    POSITION_ALGORITHM_COLUMN_NAME,
    RADIANS,
    RADIATION_MODEL_COLUMN_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    TITLE_KEY_NAME,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.hashing import generate_hash


@log_function_call
@custom_cached
def calculate_direct_normal_from_horizontal_irradiance_series(
    direct_horizontal_irradiance: ndarray,
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex | None = None,
    timezone: ZoneInfo | None = None,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    # refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> Irradiance:
    """Calculate the direct normal from the horizontal irradiance.

    The direct normal irradiance represents the amount of solar radiation
    received per unit area by a surface that is perpendicular (normal) to the
    rays that come in a straight line from the direction of the sun at its
    current position in the sky.

    This function calculates the normal irradiance from the given horizontal
    irradiance component.

    Notes
    -----
    Known also as : SID, units : W*m-2

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    solar_altitude_series = model_solar_altitude_series(
        longitude=convert_float_to_radians_if_requested(longitude, RADIANS),
        latitude=convert_float_to_radians_if_requested(latitude, RADIANS),
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        # refracted_solar_zenith=refracted_solar_zenith,
        # solar_time_model=solar_time_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
    )
    calculated_direct_normal_irradiance_series = calculate_direct_normal_from_horizontal_irradiance_series_pvgis(
        direct_horizontal_irradiance=direct_horizontal_irradiance,
        solar_altitude_series=solar_altitude_series,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )
    direct_normal_irradiance_series = calculated_direct_normal_irradiance_series.value
    print(f'Direct normal API : {direct_normal_irradiance_series}')

    # Building the output dictionary=========================================

    components_container = {
        DIRECT_NORMAL_IRRADIANCE: lambda: {
            TITLE_KEY_NAME: DIRECT_NORMAL_IRRADIANCE,
            DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME: direct_normal_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        },
        "extended": lambda: {
                TITLE_KEY_NAME: DIRECT_NORMAL_IRRADIANCE + " & horizontal component",
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: calculated_direct_normal_irradiance_series.direct_horizontal_irradiance,
            }
            if verbose > 1
            else {},
        DIRECT_NORMAL_IRRADIANCE + "relevant components": lambda: {
                ALTITUDE_COLUMN_NAME: getattr(
                    solar_altitude_series, angle_output_units
                ),
                ANGLE_UNITS_COLUMN_NAME: angle_output_units,
            }
            if verbose > 2
            else {},
        "Solar position metadata": lambda: {
                POSITION_ALGORITHM_COLUMN_NAME: solar_position_model.value,
                TIME_ALGORITHM_COLUMN_NAME: solar_time_model.value,
                PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
                ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
            }
            if verbose > 3
            else {},
        "fingerprint": lambda: {
                FINGERPRINT_COLUMN_NAME: generate_hash(direct_normal_irradiance_series.value),
            }
            if fingerprint
            else {},
    }

    components = {}
    for _, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_normal_irradiance_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
        value=direct_normal_irradiance_series.value,
        unit=IRRADIANCE_UNIT,
        position_algorithm="",
        timing_algorithm="",
        elevation=None,
        surface_orientation=None,
        surface_tilt=None,
        components=components,
    )
