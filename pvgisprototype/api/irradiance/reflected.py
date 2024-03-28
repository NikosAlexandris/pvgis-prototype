from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from rich import print
from typing import Optional
from typing import List
from .loss import calculate_angular_loss_factor_for_nondirect_irradiance
from pvgisprototype.api.geometry.models import SolarPositionModel
from pvgisprototype.api.geometry.models import SolarTimeModel
from pvgisprototype.validation.pvis_data_classes import BaseTimestampSeriesModel
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from datetime import datetime
from pathlib import Path
from math import sin
from math import cos
from pvgisprototype.api.geometry.altitude_series import model_solar_altitude_time_series
from pvgisprototype.api.irradiance.direct import calculate_direct_horizontal_irradiance_time_series
from pvgisprototype.api.irradiance.direct import calculate_extraterrestrial_normal_irradiance_time_series
from pvgisprototype.api.irradiance.diffuse import diffuse_transmission_function_time_series
from pvgisprototype.api.irradiance.diffuse import diffuse_solar_altitude_function_time_series
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
from pvgisprototype.api.series.models import MethodsForInexactMatches
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import DEGREES


@log_function_call
def calculate_ground_reflected_inclined_irradiance_time_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: BaseTimestampSeriesModel = None,
    start_time: Optional[datetime] = None,
    frequency: Optional[str] = None,
    end_time: Optional[datetime] = None,
    timezone: Optional[str] = None,
    surface_tilt: Optional[float] = SURFACE_TILT_DEFAULT,
    surface_orientation: Optional[float] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Optional[bool] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Optional[float] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: Optional[float] = MEAN_GROUND_ALBEDO_DEFAULT,
    global_horizontal_component: Optional[Path] = None,
    direct_horizontal_component: Optional[Path] = None,
    mask_and_scale: bool = False,
    neighbor_lookup: MethodsForInexactMatches = None,
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    in_memory: bool = False,
    apply_angular_loss_factor: Optional[bool] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    random_days: bool = RANDOM_DAY_FLAG_DEFAULT,
    time_output_units: str = MINUTES,
    angle_units: str = RADIANS,
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
    # if surface_tilt == 0:  # horizontally flat surface
    surface_tilt_threshold = 0.0001
    if surface_tilt <= surface_tilt_threshold:
        from pvgisprototype.validation.arrays import create_array
        shape_of_array = (
            timestamps.shape
        )
        ground_reflected_inclined_irradiance_series = create_array(
            shape_of_array, dtype=dtype, init_method="zeros", backend=array_backend
        )
        global_horizontal_irradiance_series = ground_view_fraction = (
            direct_horizontal_irradiance_series
        ) = diffuse_horizontal_irradiance_series = (
            extraterrestrial_normal_irradiance_series
        ) = solar_altitude_series = ground_reflected_irradiance_loss_factor = (
            NOT_AVAILABLE
        )

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
                calculate_direct_horizontal_irradiance_time_series(
                    longitude=longitude,
                    latitude=latitude,
                    elevation=elevation,
                    timestamps=timestamps,
                    start_time=start_time,
                    frequency=frequency,
                    end_time=end_time,
                    timezone=timezone,
                    linke_turbidity_factor_series=linke_turbidity_factor_series,
                    solar_time_model=solar_time_model,
                    time_offset_global=time_offset_global,
                    hour_offset=hour_offset,
                    solar_constant=solar_constant,
                    perigee_offset=perigee_offset,
                    eccentricity_correction_factor=eccentricity_correction_factor,
                    angle_output_units=angle_output_units,
                    dtype=dtype,
                    array_backend=array_backend,
                    verbose=0,  # no verbosity here by choice!
                    log=log,
                )
            )
            extraterrestrial_normal_irradiance_series = (
                calculate_extraterrestrial_normal_irradiance_time_series(
                    timestamps=timestamps,
                    solar_constant=solar_constant,
                    perigee_offset=perigee_offset,
                    eccentricity_correction_factor=eccentricity_correction_factor,
                    random_days=random_days,
                    dtype=dtype,
                    array_backend=array_backend,
                    verbose=0,  # no verbosity here by choice!
                    log=log,
                )
            )
            # extraterrestrial on a horizontal surface requires the solar altitude
            solar_altitude_series = model_solar_altitude_time_series(
                longitude=longitude,
                latitude=latitude,
                timestamps=timestamps,
                timezone=timezone,
                solar_position_model=solar_position_model,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                solar_time_model=solar_time_model,
                time_offset_global=time_offset_global,
                hour_offset=hour_offset,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                time_output_units=time_output_units,
                angle_units=angle_units,
                angle_output_units=angle_output_units,
                dtype=dtype,
                array_backend=array_backend,
                verbose=0,
                log=log,
            )
            diffuse_horizontal_irradiance_series = (
                extraterrestrial_normal_irradiance_series
                * diffuse_transmission_function_time_series(linke_turbidity_factor_series)
                * diffuse_solar_altitude_function_time_series(
                    solar_altitude_series, linke_turbidity_factor_series
                )
            )
            global_horizontal_irradiance_series = (
                direct_horizontal_irradiance_series + diffuse_horizontal_irradiance_series
            )

        # At this point, the global_horizontal_irradiance_series are either :
        # calculated from external time series  Or  modelled 

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
            EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: extraterrestrial_normal_irradiance_series,
            ALTITUDE_COLUMN_NAME: getattr(solar_altitude_series, angle_output_units, NOT_AVAILABLE),
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

    if verbose > 0:
        return components

    log_data_fingerprint(
        data=ground_reflected_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return ground_reflected_inclined_irradiance_series
