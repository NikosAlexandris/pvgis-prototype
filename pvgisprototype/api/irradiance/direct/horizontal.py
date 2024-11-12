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

import numpy as np
from devtools import debug
from pandas import DatetimeIndex

from pvgisprototype import Irradiance, LinkeTurbidityFactor
from pvgisprototype.api.irradiance.direct.normal import (
    calculate_direct_normal_irradiance_series,
)
from pvgisprototype.api.irradiance.direct.rayleigh_optical_thickness import (
    calculate_optical_air_mass_series,
    calculate_refracted_solar_altitude_series,
)
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SolarPositionModel,
    SolarTimeModel,
    validate_model,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ALTITUDE_COLUMN_NAME,
    ANGLE_UNITS_COLUMN_NAME,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIRECT_HORIZONTAL_IRRADIANCE,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_SOURCE_COLUMN_NAME,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_COLUMN_NAME,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    OPTICAL_AIR_MASS_COLUMN_NAME,
    PERIGEE_OFFSET,
    PERIGEE_OFFSET_COLUMN_NAME,
    POSITION_ALGORITHM_COLUMN_NAME,
    RADIANS,
    RADIATION_MODEL_COLUMN_NAME,
    REFRACTED_SOLAR_ALTITUDE_COLUMN_NAME,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    SOLAR_CONSTANT_COLUMN_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    TITLE_KEY_NAME,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array
from pvgisprototype.core.hashing import generate_hash


@log_function_call
@custom_cached
def calculate_direct_horizontal_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: DatetimeIndex | None = None,
    timezone: str | None = None,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
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
    solar_time_model = validate_model(
        SolarTimeModel, solar_time_model
    )  # can be only one of!
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
        solar_altitude_series=solar_altitude_series,  # expects altitude in degrees!
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
        verbose=verbose,
    )

    # Mask conditions -------------------------------------------------------
    mask_solar_altitude_positive = solar_altitude_series.radians > 0
    mask_not_in_shade = mask_solar_altitude_positive  # Stub, replace with actual condition !
    mask = np.logical_and.reduce((mask_solar_altitude_positive, mask_not_in_shade))

    # Initialize the direct irradiance series to zeros
    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": "zeros",
        "backend": array_backend,
    }  # Borrow shape from timestamps
    direct_horizontal_irradiance_series = create_array(**array_parameters)
    if np.any(mask):
        direct_horizontal_irradiance_series[mask] = (
            direct_normal_irradiance_series.value
            * np.sin(solar_altitude_series.radians)
        )[mask]

    # Building the output dictionary=========================================

    components_container = {
        "Metadata": lambda: {
            POSITION_ALGORITHM_COLUMN_NAME: solar_altitude_series.position_algorithm,
            TIME_ALGORITHM_COLUMN_NAME: solar_altitude_series.timing_algorithm,
            SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
        },
        DIRECT_HORIZONTAL_IRRADIANCE: lambda: {
            TITLE_KEY_NAME: DIRECT_HORIZONTAL_IRRADIANCE,
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
            IRRADIANCE_SOURCE_COLUMN_NAME: "Simulation",
        },
        DIRECT_HORIZONTAL_IRRADIANCE
        + " relevant components": lambda: (
            {
                TITLE_KEY_NAME: DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
                + " & relevant components",
                DIRECT_NORMAL_IRRADIANCE_COLUMN_NAME: direct_normal_irradiance_series.value,  # Important
                ALTITUDE_COLUMN_NAME: getattr(
                    solar_altitude_series, angle_output_units
                ),
                ANGLE_UNITS_COLUMN_NAME: angle_output_units,
            }
            if verbose > 1
            else {}
        ),
        "Atmospheric properties": lambda: (
            {
                LINKE_TURBIDITY_COLUMN_NAME: linke_turbidity_factor_series.value,
                OPTICAL_AIR_MASS_COLUMN_NAME: optical_air_mass_series.value,
                REFRACTED_SOLAR_ALTITUDE_COLUMN_NAME: (
                    refracted_solar_altitude_series.value
                    if apply_atmospheric_refraction
                    else np.full_like(refracted_solar_altitude_series.value, np.nan)
                ),  # else np.array(["-"]),
            }
            if verbose > 2
            else {}
        ),
        # "Direct normal irradiance": lambda: (
        #     {**direct_normal_irradiance_series.components}  # Merge all components
        #     if verbose > 5
        #     else {}
        # ),
        "fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    direct_horizontal_irradiance_series
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
