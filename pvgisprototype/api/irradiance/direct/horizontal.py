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

from zoneinfo import ZoneInfo
import numpy as np
from devtools import debug
from pandas import DatetimeIndex
from xarray import DataArray

from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.algorithms.hofierka.irradiance.direct.clear_sky.horizontal import calculate_clear_sky_direct_horizontal_irradiance_hofierka
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    ShadingModel,
    SolarPositionModel,
    SolarTimeModel,
    validate_model,
)
from pvgisprototype.api.position.shading import model_surface_in_shade_series
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    PERIGEE_OFFSET,
    RADIANS,
    UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
@custom_cached
def calculate_direct_horizontal_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: DatetimeIndex | None = None,
    timezone: ZoneInfo | None = None,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    # unrefracted_solar_zenith: UnrefractedSolarZenith | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    # angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
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
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        # solar_timing_model=solar_time_model,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
    )
    surface_in_shade_series = model_surface_in_shade_series(
        horizon_profile=horizon_profile,
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_time_model=solar_time_model,
        solar_position_model=solar_position_model,
        shading_model=shading_model,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        dtype=dtype,
        array_backend=array_backend,
        validate_output=validate_output,
        verbose=verbose,
        log=log,
    )
    direct_horizontal_irradiance_series = (
        calculate_clear_sky_direct_horizontal_irradiance_hofierka(
            elevation=elevation,
            timestamps=timestamps,
            solar_altitude_series=solar_altitude_series,
            surface_in_shade_series=surface_in_shade_series,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            solar_constant=solar_constant,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
        )
    )
    # direct_horizontal_irradiance_series.solar_timing_algorithm = solar_time_model.value
    # direct_horizontal_irradiance_series.solar_positioning_algorithm = solar_position_model.value
    direct_horizontal_irradiance_series.build_output(verbose, fingerprint)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=direct_horizontal_irradiance_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return direct_horizontal_irradiance_series
