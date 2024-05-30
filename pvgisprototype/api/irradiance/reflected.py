from pandas import DatetimeIndex
from pvgisprototype.api.irradiance.direct.horizontal import calculate_direct_horizontal_irradiance_series
from pvgisprototype.validation.arrays import create_array
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from typing import Optional
from .loss import calculate_angular_loss_factor_for_nondirect_irradiance
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pathlib import Path
from math import sin
from math import cos
from pvgisprototype.api.irradiance.diffuse.horizontal import calculate_diffuse_horizontal_irradiance_series
from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_COLUMN_NAME
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_COLUMN_NAME
from pvgisprototype.constants import ANGLE_UNITS_COLUMN_NAME
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import MEAN_GROUND_ALBEDO_DEFAULT
from pvgisprototype.constants import ANGULAR_LOSS_FACTOR_FLAG_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import RANDOM_DAY_FLAG_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import TITLE_KEY_NAME
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import MINUTES
from pvgisprototype.constants import REFLECTED_INCLINED_IRRADIANCE
from pvgisprototype.constants import REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import ALBEDO_COLUMN_NAME
from pvgisprototype.constants import GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import VIEW_FRACTION_COLUMN_NAME
from pvgisprototype.constants import LOSS_COLUMN_NAME
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import ALTITUDE_COLUMN_NAME
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype.validation.hashing import generate_hash
from pvgisprototype.api.series.select import select_time_series
from pvgisprototype.api.series.models import MethodForInexactMatches
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import DEGREES
from pvgisprototype import Irradiance
from pvgisprototype.constants import RADIATION_MODEL_COLUMN_NAME
from pvgisprototype.constants import HOFIERKA_2002


@log_function_call
def calculate_ground_reflected_inclined_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: DatetimeIndex = None,
    timezone: Optional[str] = None,
    surface_orientation: float = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: float = SURFACE_TILT_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Optional[bool] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Optional[float] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: Optional[float] = MEAN_GROUND_ALBEDO_DEFAULT,
    global_horizontal_component: Optional[Path] = None,
    mask_and_scale: bool = False,
    neighbor_lookup: MethodForInexactMatches = None,
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    in_memory: bool = False,
    apply_angular_loss_factor: Optional[bool] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
):
    """Calculate the clear-sky diffuse ground reflected irradiance on an inclined surface (Ri).

    The calculation relies on an isotropic assumption. The ground reflected
    clear-sky irradiance received on an inclined surface [W.m-2] is
    proportional to the global horizontal irradiance Ghc, to the mean ground
    albedo ρg and a fraction of the ground viewed by an inclined surface
    rg(γN).
    """
    # in order to avoid 'NameError's
    import numpy
    direct_horizontal_irradiance_series = create_array(
        timestamps.shape, dtype=dtype, init_method=numpy.nan, backend=array_backend
    )
    diffuse_horizontal_irradiance_series = create_array(
        timestamps.shape, dtype=dtype, init_method=numpy.nan, backend=array_backend
    )
    # if surface_tilt == 0:  # horizontally flat surface
    surface_tilt_threshold = 0.0001
    if surface_tilt <= surface_tilt_threshold:
        shape_of_array = (
            timestamps.shape
        )
        ground_reflected_inclined_irradiance_series = create_array(
            shape_of_array, dtype=dtype, init_method="zeros", backend=array_backend
        )
        global_horizontal_irradiance_series = NOT_AVAILABLE 
        ground_view_fraction = NOT_AVAILABLE
        ground_reflected_irradiance_loss_factor = NOT_AVAILABLE

    else:
        # - based on external global and direct irradiance components
        if global_horizontal_component:
            global_horizontal_irradiance_series = select_time_series(
                time_series=global_horizontal_component,
                longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
                latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
                timestamps=timestamps,
                mask_and_scale=mask_and_scale,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                in_memory=in_memory,
                log=log,
            ).to_numpy().astype(dtype=dtype)
        else:  # or from the model
            direct_horizontal_irradiance_series = (
                calculate_direct_horizontal_irradiance_series(
                    longitude=longitude,
                    latitude=latitude,
                    elevation=elevation,
                    timestamps=timestamps,
                    timezone=timezone,
                    linke_turbidity_factor_series=linke_turbidity_factor_series,
                    solar_time_model=solar_time_model,
                    solar_constant=solar_constant,
                    perigee_offset=perigee_offset,
                    eccentricity_correction_factor=eccentricity_correction_factor,
                    angle_output_units=angle_output_units,
                    dtype=dtype,
                    array_backend=array_backend,
                    verbose=verbose,  # verbosity here ?
                    log=log,
                )
            ).value  # Important !
            diffuse_horizontal_irradiance_series = (
                calculate_diffuse_horizontal_irradiance_series(
                    longitude=longitude,
                    latitude=latitude,
                    timestamps=timestamps,
                    timezone=timezone,
                    linke_turbidity_factor_series=linke_turbidity_factor_series,
                    apply_atmospheric_refraction=apply_atmospheric_refraction,
                    refracted_solar_zenith=refracted_solar_zenith,
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
            ).value  # Important !
            global_horizontal_irradiance_series = (
                direct_horizontal_irradiance_series + diffuse_horizontal_irradiance_series
            )

        # At this point, the global_horizontal_irradiance_series are either :
        # _read_ from external time series  Or estimated from the solar
        # radiation model by Hofierka (2002)

        # clear-sky ground reflected irradiance
        ground_view_fraction = (1 - cos(surface_tilt)) / 2
        ground_reflected_inclined_irradiance_series = (
            albedo * global_horizontal_irradiance_series * ground_view_fraction
        )

        if apply_angular_loss_factor:
            ground_reflected_irradiance_angular_loss_coefficient = sin(surface_tilt) + (
                surface_tilt - sin(surface_tilt)
            ) / (1 - cos(surface_tilt))
            ground_reflected_irradiance_loss_factor = calculate_angular_loss_factor_for_nondirect_irradiance(
                indirect_angular_loss_coefficient=ground_reflected_irradiance_angular_loss_coefficient,
            )
            ground_reflected_inclined_irradiance_series *= (
                ground_reflected_irradiance_loss_factor
            )

    components_container = {
        'main': lambda: {
            TITLE_KEY_NAME: REFLECTED_INCLINED_IRRADIANCE,
            REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME: ground_reflected_inclined_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        },

        'extended': lambda: {
            LOSS_COLUMN_NAME: 1 - ground_reflected_irradiance_loss_factor if apply_angular_loss_factor and not all(ground_reflected_inclined_irradiance_series == 0) else 0 if all(ground_reflected_inclined_irradiance_series == 0) else '-',
            SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(surface_tilt, angle_output_units),
            SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(surface_orientation, angle_output_units),
            ANGLE_UNITS_COLUMN_NAME: angle_output_units,
        } if verbose > 1 else {},

        'more_extended': lambda: {
            ALBEDO_COLUMN_NAME: albedo,
            GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: global_horizontal_irradiance_series,
            VIEW_FRACTION_COLUMN_NAME: ground_view_fraction,
        } if verbose > 2 else {},

        'even_more_extended': lambda: {
            TITLE_KEY_NAME: REFLECTED_INCLINED_IRRADIANCE + " & horizontal components",
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: direct_horizontal_irradiance_series,
            DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_horizontal_irradiance_series,
        } if verbose > 3 else {},

        'and_even_more_extended': lambda: {
        } if verbose > 4 else {},

        'extra': lambda: {
        } if verbose > 5 else {},

        'fingerprint': lambda: {
            FINGERPRINT_COLUMN_NAME: generate_hash(ground_reflected_inclined_irradiance_series),
        } if fingerprint else {},
    }

    components = {}
    for key, component in components_container.items():
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
            unit=IRRADIANCE_UNITS,
            position_algorithm="",
            timing_algorithm="",
            elevation=elevation,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            components=components,
            )
