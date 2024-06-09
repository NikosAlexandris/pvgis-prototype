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
from typing import Optional
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
from pvgisprototype.api.position.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.irradiance.models import DirectIrradianceComponents
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.irradiance.shade import is_surface_in_shade_series
from pvgisprototype.api.irradiance.direct.normal import calculate_direct_normal_irradiance_series
from pvgisprototype.api.irradiance.direct.rayleigh_optical_thickness import calculate_refracted_solar_altitude_series
from pvgisprototype.api.irradiance.direct.rayleigh_optical_thickness import calculate_optical_air_mass_series
from pvgisprototype.api.irradiance.limits import LOWER_PHYSICALLY_POSSIBLE_LIMIT
from pvgisprototype.api.irradiance.limits import UPPER_PHYSICALLY_POSSIBLE_LIMIT
# from pvgisprototype.api.utilities.progress import progress
# from rich.progress import Progress
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_to_degrees_if_requested
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.cli.print import print_irradiance_table_2
from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME, NO_SOLAR_INCIDENCE, NOT_AVAILABLE
from pvgisprototype.constants import TITLE_KEY_NAME
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ALTITUDE_COLUMN_NAME
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
from pvgisprototype.constants import IRRADIANCE_UNIT
from pvgisprototype.constants import ANGLE_UNITS_COLUMN_NAME
from pvgisprototype.constants import DEGREES
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import IRRADIANCE_SOURCE_COLUMN_NAME
from pvgisprototype.constants import RADIATION_MODEL_COLUMN_NAME
from pvgisprototype.constants import HOFIERKA_2002
from pvgisprototype.constants import LONGITUDE_COLUMN_NAME
from pvgisprototype.constants import LATITUDE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_NORMAL_IRRADIANCE
from pvgisprototype.constants import DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import LOSS_COLUMN_NAME
from pvgisprototype.constants import SURFACE_TILT_COLUMN_NAME
from pvgisprototype.constants import SURFACE_ORIENTATION_COLUMN_NAME
from pvgisprototype.constants import INCIDENCE_COLUMN_NAME
from pvgisprototype.constants import ALTITUDE_COLUMN_NAME
from pvgisprototype.constants import INCIDENCE_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import INCIDENCE_DEFINITION
from pvgisprototype.constants import POSITION_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import TIME_ALGORITHM_COLUMN_NAME
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
def calculate_direct_horizontal_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: DatetimeIndex = None,
    timezone: Optional[str] = None,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: Optional[bool] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Optional[float] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_COLUMN_NAME,
) -> np.ndarray:
    """Calculate the direct horizontal irradiance

    This function implements the algorithm described by Hofierka [1]_.

    Notes
    -----
    Known also as : SID, units : W*m-2

    References
    ----------
    .. [1] Hofierka, J. (2002). Some title of the paper. Journal Name, vol(issue), pages.

    """
    solar_time_model = validate_model(SolarTimeModel, solar_time_model)  # can be only one of!
    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
    )
    
    # expects solar altitude in degrees! ----------------------------------vvv
    refracted_solar_altitude_series = calculate_refracted_solar_altitude_series(
        solar_altitude_series=solar_altitude_series,   # expects altitude in degrees!
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    optical_air_mass_series = calculate_optical_air_mass_series(
        elevation=elevation,
        refracted_solar_altitude_series=refracted_solar_altitude_series,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    # ^^^ --------------------------------- expects solar altitude in degrees!
    direct_normal_irradiance_series = calculate_direct_normal_irradiance_series(
        timestamps=timestamps,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        optical_air_mass_series=optical_air_mass_series,
        solar_constant=solar_constant,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
    )

    # Mask conditions -------------------------------------------------------
    mask_solar_altitude_positive = solar_altitude_series.radians > 0
    mask_not_in_shade = np.full_like(solar_altitude_series.radians, True)  # Stub, replace with actual condition
    mask = np.logical_and.reduce((mask_solar_altitude_positive, mask_not_in_shade))

    # Initialize the direct irradiance series to zeros
    direct_horizontal_irradiance_series = np.zeros_like(solar_altitude_series.radians)
    if np.any(mask):
        direct_horizontal_irradiance_series[mask] = (
            direct_normal_irradiance_series.value * np.sin(solar_altitude_series.radians)
        )[mask]

    # Building the output dictionary=========================================

    components_container = {
        'main': lambda: {
            TITLE_KEY_NAME: DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
            IRRADIANCE_SOURCE_COLUMN_NAME: 'Simulation',
        },

        'extended': lambda: {
            TITLE_KEY_NAME: DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME + ' & relevant components',
            DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME: direct_normal_irradiance_series.value,  # Important
            ALTITUDE_COLUMN_NAME: getattr(solar_altitude_series, angle_output_units),
            ANGLE_UNITS_COLUMN_NAME: angle_output_units,
        } if verbose > 1 else {},

        'more_extended': lambda: {
            LINKE_TURBIDITY_COLUMN_NAME: linke_turbidity_factor_series.value,
            OPTICAL_AIR_MASS_COLUMN_NAME: optical_air_mass_series.value,
            REFRACTED_SOLAR_ALTITUDE_COLUMN_NAME: refracted_solar_altitude_series.value if apply_atmospheric_refraction else np.full_like(refracted_solar_altitude_series.value, np.nan),#else np.array(["-"]),
        } if verbose > 2 else {},

        'even_more_extended': lambda: {
            POSITION_ALGORITHM_COLUMN_NAME: solar_position_model.value,
            TIME_ALGORITHM_COLUMN_NAME: solar_time_model.value,
            # "Shade": in_shade,
        } if verbose > 3 else {},

        'and_even_more_extended': lambda: {
            SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
        } if verbose > 4 else {},

        'fingerprint': lambda: {
            FINGERPRINT_COLUMN_NAME: generate_hash(direct_horizontal_irradiance_series),
        } if fingerprint else {},
    }

    components = {}
    for _, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
            value=direct_horizontal_irradiance_series,
            unit=IRRADIANCE_UNIT,
            position_algorithm=solar_position_model.value,
            timing_algorithm=solar_time_model.value,
            elevation=elevation,
            surface_orientation=None,
            surface_tilt=None,
            data_source=HOFIERKA_2002,
            components=components,
            )
