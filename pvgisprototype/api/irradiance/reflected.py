from math import cos, sin
from pathlib import Path

from devtools import debug
from numpy import ndarray, where
from pandas import DatetimeIndex

from pvgisprototype import Irradiance, LinkeTurbidityFactor
from pvgisprototype.algorithms.pvis.ground_reflected import calculate_ground_reflected_inclined_irradiance_series_pvgis
from pvgisprototype.api.irradiance.reflectivity import (
    calculate_reflectivity_effect,
    calculate_reflectivity_effect_percentage,
    calculate_reflectivity_factor_for_nondirect_irradiance,
)
from pvgisprototype.api.position.models import SolarPositionModel, SolarTimeModel
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.constants import (
    ALBEDO_COLUMN_NAME,
    ALBEDO_DEFAULT,
    ANGLE_UNITS_COLUMN_NAME,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DEGREES,
    DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    PERIGEE_OFFSET,
    RADIANS,
    RADIATION_MODEL_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE,
    REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME,
    REFLECTIVITY_COLUMN_NAME,
    REFLECTIVITY_FACTOR_COLUMN_NAME,
    REFLECTIVITY_PERCENTAGE_COLUMN_NAME,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    TITLE_KEY_NAME,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    VIEW_FRACTION_COLUMN_NAME,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array
from pvgisprototype.core.hashing import generate_hash


def apply_reflectivity_factor_for_nondirect_irradiance(
    ground_reflected_inclined_irradiance_series: ndarray,
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
):
    """
    This isn't the cleanest solution ever ! ------------------------- ReviewMe

    """
    ground_reflected_irradiance_reflectivity_coefficient = sin(surface_tilt) + (
        surface_tilt - sin(surface_tilt)
    ) / (1 - cos(surface_tilt))
    ground_reflected_irradiance_reflectivity_factor = calculate_reflectivity_factor_for_nondirect_irradiance(
        indirect_angular_loss_coefficient=ground_reflected_irradiance_reflectivity_coefficient,
    )
    ground_reflected_irradiance_reflectivity_factor_series = create_array(
        ground_reflected_inclined_irradiance_series.shape,
        dtype=dtype,
        init_method=ground_reflected_irradiance_reflectivity_factor,
        backend=array_backend,
    )
    ground_reflected_inclined_irradiance_series *= (
        ground_reflected_irradiance_reflectivity_factor_series
    )
    ground_reflected_inclined_irradiance_before_reflectivity_series = where(
        ground_reflected_irradiance_reflectivity_factor_series != 0,
        ground_reflected_inclined_irradiance_series
        / ground_reflected_irradiance_reflectivity_factor_series,
        0,
    )
    reflectivity_effect = calculate_reflectivity_effect(
        irradiance=ground_reflected_inclined_irradiance_before_reflectivity_series,
        reflectivity=ground_reflected_irradiance_reflectivity_factor_series,
    )
    reflectivity_effect_percentage = calculate_reflectivity_effect_percentage(
        irradiance=ground_reflected_inclined_irradiance_before_reflectivity_series,
        reflectivity=ground_reflected_irradiance_reflectivity_factor_series,
    )

    return (
        ground_reflected_inclined_irradiance_series,
        ground_reflected_irradiance_reflectivity_factor_series,
        ground_reflected_inclined_irradiance_before_reflectivity_series,
        reflectivity_effect,
        reflectivity_effect_percentage,
    )


@log_function_call
def calculate_ground_reflected_inclined_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: DatetimeIndex | None = None,
    timezone: str | None = None,
    surface_orientation: float = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    surface_tilt_threshold = SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,  # Changed this to np.ndarray
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: float | None = ALBEDO_DEFAULT,
    global_horizontal_component: Path | None = None,
    mask_and_scale: bool = False,
    neighbor_lookup: MethodForInexactMatches = None,
    tolerance: float | None = TOLERANCE_DEFAULT,
    in_memory: bool = False,
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
):
    """Calculate the clear-sky diffuse ground reflected irradiance on an inclined surface (Ri).

    The calculation relies on an isotropic assumption. The ground reflected
    clear-sky irradiance received on an inclined surface [W.m-2] is
    proportional to the global horizontal irradiance Ghc, to the mean ground
    albedo ρg and a fraction of the ground viewed by an inclined surface
    rg(γN).

    """
    # in order to avoid 'NameError's
    position_algorithm = NOT_AVAILABLE
    timing_algorithm = NOT_AVAILABLE

    # Default array parameters
    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "backend": array_backend,
        "init_method": "zeros" if surface_tilt <= surface_tilt_threshold else "empty"
    }
    # In order to avoid unbound errors
    direct_horizontal_irradiance_series = create_array(**array_parameters)
    diffuse_horizontal_irradiance_series = create_array(**array_parameters)

    if global_horizontal_component:
        global_horizontal_irradiance_series = (
            select_time_series(
                time_series=global_horizontal_component,
                longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
                latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
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
    else:
        global_horizontal_irradiance_series = None

    calculated_ground_reflected_inclined_irradiance_series = (
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
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            refracted_solar_zenith=refracted_solar_zenith,
            albedo=albedo,
            global_horizontal_irradiance_series=global_horizontal_irradiance_series,
            solar_position_model=solar_position_model,
            solar_time_model=solar_time_model,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            angle_output_units=angle_output_units,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
        )
    )  # Important !

    if apply_reflectivity_factor:
        (
            ground_reflected_inclined_irradiance_series,
            ground_reflected_irradiance_reflectivity_factor_series,
            ground_reflected_inclined_irradiance_before_reflectivity_series,
            reflectivity_effect,
            reflectivity_effect_percentage,
        ) = apply_reflectivity_factor_for_nondirect_irradiance(
            ground_reflected_inclined_irradiance_series=calculated_ground_reflected_inclined_irradiance_series.value,
            surface_tilt=surface_tilt,
            dtype=dtype,
            array_backend=array_backend,
        )

    components_container = {
        "Ground-reflected Diffuse Inclined Irradiance": lambda: {
            TITLE_KEY_NAME: REFLECTED_INCLINED_IRRADIANCE,
            REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME: ground_reflected_inclined_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        },
        "Reflectivity effect": lambda: (
            {
                # Attention : input irradiance _before_ reflectivity effect !
                REFLECTIVITY_COLUMN_NAME: (
                    reflectivity_effect
                    if reflectivity_effect is not None
                    else None
                ),
                REFLECTIVITY_PERCENTAGE_COLUMN_NAME: (
                    reflectivity_effect_percentage
                    if reflectivity_effect_percentage is not None
                    else None
                ),
            }
            if verbose > 6 and apply_reflectivity_factor
            else {}
        ),
        "Reflectivity factor": lambda: (
            {
                # REFLECTIVITY_FACTOR_COLUMN_NAME: where(ground_reflected_irradiance_reflectivity_factor_series <= 0, 0, (1 - ground_reflected_irradiance_reflectivity_factor_series)),
                REFLECTIVITY_FACTOR_COLUMN_NAME: (
                    ground_reflected_irradiance_reflectivity_factor_series
                    if ground_reflected_irradiance_reflectivity_factor_series.any()
                    else None
                ),
                REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: (
                    ground_reflected_inclined_irradiance_before_reflectivity_series
                    if ground_reflected_inclined_irradiance_before_reflectivity_series.any()
                    else None
                ),
                # } if verbose > 1 and apply_reflectivity_factor else {},
            }
            if apply_reflectivity_factor
            else {}
        ),
        "Metadata": lambda: (
            {
                VIEW_FRACTION_COLUMN_NAME: calculated_ground_reflected_inclined_irradiance_series.ground_view_fraction,
                ALBEDO_COLUMN_NAME: albedo,
                GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: global_horizontal_irradiance_series,
            }
            if verbose > 2
            else {}
        ),
        "Surface position": lambda: (
            {
                SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_tilt, angle_output_units
                ),
                SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_orientation, angle_output_units
                ),
                ANGLE_UNITS_COLUMN_NAME: angle_output_units,
            }
            if verbose > 3
            else {}
        ),
        "Irradiance Metadata": lambda: (
            {
                TITLE_KEY_NAME: REFLECTED_INCLINED_IRRADIANCE
                + " & horizontal components",
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
                DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series,
            }
            if verbose > 4
            else {}
        ),
        "Fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    ground_reflected_inclined_irradiance_series
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
        data=ground_reflected_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
        value=ground_reflected_inclined_irradiance_series,
        unit=IRRADIANCE_UNIT,
        position_algorithm=position_algorithm,
        timing_algorithm=timing_algorithm,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        components=components,
    )
