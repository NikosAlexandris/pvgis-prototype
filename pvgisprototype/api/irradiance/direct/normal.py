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
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
import numpy as np
from pvgisprototype import SolarAltitude
from pvgisprototype import RefractedSolarAltitude
from pvgisprototype import OpticalAirMass
from pvgisprototype import RayleighThickness
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype import Elevation
from pvgisprototype import Irradiance
from pvgisprototype.validation.functions import validate_with_pydantic
from pvgisprototype.validation.functions import AdjustElevationInputModel
from pvgisprototype.validation.functions import CalculateOpticalAirMassTimeSeriesInputModel
from pvgisprototype.api.position.models import validate_model
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.incidence import model_solar_incidence_series
from pvgisprototype.api.irradiance.models import DirectIrradianceComponents
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.irradiance.shade import is_surface_in_shade_series
from pvgisprototype.api.irradiance.direct.linke_turbidity_factor import correct_linke_turbidity_factor_series
from pvgisprototype.api.irradiance.direct.rayleigh_optical_thickness import calculate_rayleigh_optical_thickness_series
from pvgisprototype.api.irradiance.extraterrestrial import calculate_extraterrestrial_normal_irradiance_series
from pvgisprototype.api.irradiance.limits import LOWER_PHYSICALLY_POSSIBLE_LIMIT
from pvgisprototype.api.irradiance.limits import UPPER_PHYSICALLY_POSSIBLE_LIMIT
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME
from pvgisprototype.constants import TITLE_KEY_NAME
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import SOLAR_CONSTANT_COLUMN_NAME
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import PERIGEE_OFFSET_COLUMN_NAME
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import LINKE_TURBIDITY_UNIT
from pvgisprototype.constants import LINKE_TURBIDITY_COLUMN_NAME
from pvgisprototype.constants import LINKE_TURBIDITY_ADJUSTED_COLUMN_NAME
from pvgisprototype.constants import OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT
from pvgisprototype.constants import OPTICAL_AIR_MASS_UNIT
from pvgisprototype.constants import OPTICAL_AIR_MASS_COLUMN_NAME
from pvgisprototype.constants import RAYLEIGH_OPTICAL_THICKNESS_UNIT
from pvgisprototype.constants import RAYLEIGH_OPTICAL_THICKNESS_COLUMN_NAME
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import ANGLE_UNITS_COLUMN_NAME
from pvgisprototype.constants import DEGREES
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import IRRADIANCE_SOURCE_COLUMN_NAME
from pvgisprototype.constants import RADIATION_MODEL_COLUMN_NAME
from pvgisprototype.constants import HOFIERKA_2002
from pvgisprototype.constants import DIRECT_NORMAL_IRRADIANCE
from pvgisprototype.constants import DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME
from pandas import DatetimeIndex
from cachetools import cached
from pvgisprototype.caching import custom_hashkey
from pvgisprototype.validation.hashing import generate_hash
from pvgisprototype.constants import RANDOM_TIMESTAMPS_FLAG_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import INDEX_IN_TABLE_OUTPUT_FLAG_DEFAULT


@log_function_call
@cached(cache={}, key=custom_hashkey)
def calculate_direct_normal_irradiance_series(
    timestamps: DatetimeIndex = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    optical_air_mass_series: OpticalAirMass = [OPTICAL_AIR_MASS_TIME_SERIES_DEFAULT], # REVIEW-ME + ?
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
) -> np.array:
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
    extraterrestrial_normal_irradiance_series = (
        calculate_extraterrestrial_normal_irradiance_series(
            timestamps=timestamps,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
        )
    )
    corrected_linke_turbidity_factor_series = correct_linke_turbidity_factor_series(
        linke_turbidity_factor_series,
        verbose=verbose,
    )
    rayleigh_optical_thickness_series = calculate_rayleigh_optical_thickness_series(
        optical_air_mass_series,
        verbose=verbose,
    )  # _quite_ high when the sun is below the horizon. Makes sense ?

    # Calculate
    direct_normal_irradiance_series = (
        extraterrestrial_normal_irradiance_series.value
        * np.exp(
            corrected_linke_turbidity_factor_series.value
            * optical_air_mass_series.value
            * rayleigh_optical_thickness_series.value
        )
    )
    # Warning
    if (
        (direct_normal_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT)
        | (direct_normal_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
    ).any():
        out_of_range_values = direct_normal_irradiance_series[
            (direct_normal_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT)
            | (direct_normal_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
        ]
        warning_unstyled = (
                f"\n"
                f"{WARNING_OUT_OF_RANGE_VALUES} "
                f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
                f" in direct_normal_irradiance_series : "
                f"{out_of_range_values}"
                f"\n"
                )
        warning = (
                f"\n"
                f"{WARNING_OUT_OF_RANGE_VALUES} "
                f"[{LOWER_PHYSICALLY_POSSIBLE_LIMIT}, {UPPER_PHYSICALLY_POSSIBLE_LIMIT}]"
                f" in [code]direct_normal_irradiance_series[/code] : "
                f"{out_of_range_values}"
                f"\n"
                )
        logger.warning(warning_unstyled, alt=warning)

    # Building the output dictionary=========================================

    components_container = {
        'main': lambda: {
            TITLE_KEY_NAME: DIRECT_NORMAL_IRRADIANCE,
            DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME: direct_normal_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        },

        'extended': lambda: {
            TITLE_KEY_NAME: DIRECT_NORMAL_IRRADIANCE + ' & relevant components',
            EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: extraterrestrial_normal_irradiance_series.value,
        } if verbose > 1 else {},

        'more_extended': lambda: {
            LINKE_TURBIDITY_ADJUSTED_COLUMN_NAME: corrected_linke_turbidity_factor_series.value,
            LINKE_TURBIDITY_COLUMN_NAME: linke_turbidity_factor_series.value,
            RAYLEIGH_OPTICAL_THICKNESS_COLUMN_NAME: rayleigh_optical_thickness_series.value,
            OPTICAL_AIR_MASS_COLUMN_NAME: optical_air_mass_series.value,
        } if verbose > 2 else {},

        'even_more_extended': lambda: {
            SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
        } if verbose > 3 else {},

        'fingerprint': lambda: {
            FINGERPRINT_COLUMN_NAME: generate_hash(direct_normal_irradiance_series),
        } if fingerprint else {},
    }

    components = {}
    for key, component in components_container.items():
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
            unit=IRRADIANCE_UNITS,
            position_algorithm="",
            timing_algorithm="",
            elevation=None,
            surface_orientation=None,
            surface_tilt=None,
            components=components,
            )
