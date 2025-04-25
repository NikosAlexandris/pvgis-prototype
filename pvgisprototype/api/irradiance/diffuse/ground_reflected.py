from zoneinfo import ZoneInfo
from devtools import debug
from numpy import ndarray
from pandas import DatetimeIndex, Timestamp
from pvgisprototype import LinkeTurbidityFactor, GroundReflectedInclinedIrradiance
from pvgisprototype.algorithms.hofierka.irradiance.diffuse.ground_reflected import calculate_ground_reflected_inclined_irradiance_series_pvgis
from pvgisprototype.api.irradiance.reflectivity import apply_reflectivity_factor_for_nondirect_irradiance
from pvgisprototype.api.position.models import SolarPositionModel, SolarTimeModel
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
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
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
@custom_cached
def calculate_ground_reflected_inclined_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo | None = None,
    surface_orientation: float = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    surface_tilt_threshold = SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,  # Changed this to np.ndarray
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: (
        float | None
    ) = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: float | None = ALBEDO_DEFAULT,
    global_horizontal_irradiance: ndarray | None = None,
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> GroundReflectedInclinedIrradiance:
    """Calculate the clear-sky diffuse ground reflected irradiance on an inclined surface (Ri).

    The calculation relies on an isotropic assumption. The ground reflected
    clear-sky irradiance received on an inclined surface [W.m-2] is
    proportional to the global horizontal irradiance Ghc, to the mean ground
    albedo ρg and a fraction of the ground viewed by an inclined surface
    rg(γN).

    """
    ground_reflected_inclined_irradiance_series = GroundReflectedInclinedIrradiance(ground_view_fraction=0)
    if surface_tilt != 0:
        ground_reflected_inclined_irradiance_series = (
            calculate_ground_reflected_inclined_irradiance_series_pvgis(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                timestamps=timestamps,
                timezone=timezone,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                surface_tilt_threshold=surface_tilt_threshold,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                albedo=albedo,
                global_horizontal_irradiance=global_horizontal_irradiance,
                solar_position_model=solar_position_model,
                solar_time_model=solar_time_model,
                solar_constant=solar_constant,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                angle_output_units=angle_output_units,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                fingerprint=fingerprint,
            )
        )
        if apply_reflectivity_factor:
            ground_reflected_inclined_irradiance_series = apply_reflectivity_factor_for_nondirect_irradiance(
                ground_reflected_inclined_irradiance_series=ground_reflected_inclined_irradiance_series,
                surface_tilt=surface_tilt,
                dtype=dtype,
                array_backend=array_backend,
            )

    ground_reflected_inclined_irradiance_series.build_output(verbose, fingerprint)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=ground_reflected_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return ground_reflected_inclined_irradiance_series
