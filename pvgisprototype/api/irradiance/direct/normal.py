"""
This Python module is part of PVGIS' API. It implements functions to calculate
the direct solar irradiance.

_Direct_ or _beam_ irradiance is one of the main components of solar
irradiance. It comes perpendicular from the Sun and is not scattered before it
irradiates a surface.

During a cloudy day the sunlight will be partially absorbed and scattered by
different air molecules. The latter part is defined as the _diffuse_
irradiance. The remaining part is the _direct_ irradiance.
"""

from pathlib import Path
from zoneinfo import ZoneInfo

from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import (
    Irradiance,
    Latitude,
    LinkeTurbidityFactor,
    Longitude,
    OpticalAirMass,
)
from pvgisprototype.algorithms.pvis.direct.normal import (
    calculate_direct_normal_irradiance_series_pvgis,
    calculate_direct_normal_from_horizontal_irradiance_series_pvgis,
)
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.series.select import select_time_series
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
    EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IN_MEMORY_FLAG_DEFAULT,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_ADJUSTED_COLUMN_NAME,
    LINKE_TURBIDITY_COLUMN_NAME,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    MASK_AND_SCALE_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    OPTICAL_AIR_MASS_COLUMN_NAME,
    OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT,
    OUT_OF_RANGE_INDICES_COLUMN_NAME,
    PERIGEE_OFFSET,
    PERIGEE_OFFSET_COLUMN_NAME,
    POSITION_ALGORITHM_COLUMN_NAME,
    RADIANS,
    RADIATION_MODEL_COLUMN_NAME,
    RAYLEIGH_OPTICAL_THICKNESS_COLUMN_NAME,
    SOLAR_CONSTANT,
    SOLAR_CONSTANT_COLUMN_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    TITLE_KEY_NAME,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.hashing import generate_hash


@log_function_call
@custom_cached
def calculate_direct_normal_irradiance_series(
    timestamps: DatetimeIndex | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    optical_air_mass_series: OpticalAirMass = [
        OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT
    ],  # REVIEW-ME + ?
    clip_to_physically_possible_limits: bool = True,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> Irradiance:
    """Calculate the direct normal irradiance.

    The direct normal irradiance represents the amount of solar radiation
    received per unit area by a surface that is perpendicular (normal) to the
    rays that come in a straight line from the direction of the sun at its
    current position in the sky.

    This function implements the algorithm described by Hofierka, 2002. [1]_

    Notes
    -----
    Known also as : SID, units : W*m-2

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    direct_normal_irradiance_series = calculate_direct_normal_irradiance_series_pvgis(
            timestamps=timestamps,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            optical_air_mass_series=optical_air_mass_series,
            clip_to_physically_possible_limits=clip_to_physically_possible_limits,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
            )

    # Building the output dictionary=========================================

    components_container = {
        "Metadata": lambda: {
            SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
        },
        DIRECT_NORMAL_IRRADIANCE: lambda: {
            TITLE_KEY_NAME: DIRECT_NORMAL_IRRADIANCE,
            DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME: direct_normal_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        },
        DIRECT_NORMAL_IRRADIANCE
        + " & relevant components": lambda: (
            {
                TITLE_KEY_NAME: DIRECT_NORMAL_IRRADIANCE + " & relevant components",
                EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: direct_normal_irradiance_series.extraterrestrial_normal_irradiance,
            }
            if verbose > 1
            else {}
        ),
        "Atmospheric properties": lambda: (
            {
                LINKE_TURBIDITY_ADJUSTED_COLUMN_NAME: direct_normal_irradiance_series.linke_turbidity_factor_adjusted,
                LINKE_TURBIDITY_COLUMN_NAME: linke_turbidity_factor_series.value,
                RAYLEIGH_OPTICAL_THICKNESS_COLUMN_NAME: direct_normal_irradiance_series.rayleigh_optical_thickness,
                OPTICAL_AIR_MASS_COLUMN_NAME: optical_air_mass_series.value,
            }
            if verbose > 2
            else {}
        ),
        "Out-of-range": lambda: (
            {
                OUT_OF_RANGE_INDICES_COLUMN_NAME: direct_normal_irradiance_series.out_of_range,
                OUT_OF_RANGE_INDICES_COLUMN_NAME + " i": direct_normal_irradiance_series.out_of_range_index,
            }
            if direct_normal_irradiance_series.out_of_range.size > 0
            else {}
        ),
        "Fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(direct_normal_irradiance_series),
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
        data=direct_normal_irradiance_series,
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


@log_function_call
@custom_cached
def calculate_direct_normal_from_horizontal_irradiance_series(
    direct: Path,
    longitude: Longitude,
    latitude: Latitude,
    timestamps: DatetimeIndex | None = None,
    timezone: ZoneInfo | None = None,
    neighbor_lookup: MethodForInexactMatches = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: float | None = TOLERANCE_DEFAULT,
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
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
    fingerprint: bool = False,
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
            log=log,
        )
        .to_numpy()
        .astype(dtype=dtype)
    )
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
    direct_horizontal_irradiance_series = calculate_direct_normal_from_horizontal_irradiance_series_pvgis(
        direct_horizontal_irradiance=direct_horizontal_irradiance_series,
        solar_altitude_series=solar_altitude_series,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )

    # Building the output dictionary=========================================

    components_container = {
        "main": lambda: {
            TITLE_KEY_NAME: DIRECT_NORMAL_IRRADIANCE,
            DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME: direct_normal_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        },
        "extended": lambda: (
            {
                TITLE_KEY_NAME: DIRECT_NORMAL_IRRADIANCE + " & horizontal component",
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
            }
            if verbose > 1
            else {}
        ),
        "more_extended": lambda: (
            {
                ALTITUDE_COLUMN_NAME: getattr(
                    solar_altitude_series, angle_output_units
                ),
                ANGLE_UNITS_COLUMN_NAME: angle_output_units,
            }
            if verbose > 2
            else {}
        ),
        "even_more_extended": lambda: (
            {
                POSITION_ALGORITHM_COLUMN_NAME: solar_position_model.value,
                TIME_ALGORITHM_COLUMN_NAME: solar_time_model.value,
            }
            if verbose > 3
            else {}
        ),
        "fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(direct_normal_irradiance_series),
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
        data=direct_normal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
        value=direct_normal_irradiance_series,
        unit=IRRADIANCE_UNIT,
        position_algorithm="",
        timing_algorithm="",
        elevation=None,
        surface_orientation=None,
        surface_tilt=None,
        components=components,
    )
