"""
API module to calculate the global (shortwave) irradiance over a
location for a period in time.
"""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy
from devtools import debug

from pvgisprototype import Irradiance, LinkeTurbidityFactor
from pvgisprototype.api.irradiance.diffuse.inclined import (
    calculate_diffuse_inclined_irradiance_series,
)
from pvgisprototype.api.irradiance.direct.inclined import (
    calculate_direct_inclined_irradiance_series_pvgis,
)
from pvgisprototype.api.irradiance.limits import (
    LOWER_PHYSICALLY_POSSIBLE_LIMIT,
    UPPER_PHYSICALLY_POSSIBLE_LIMIT,
)
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.irradiance.reflected import (
    calculate_ground_reflected_inclined_irradiance_series,
)
from pvgisprototype.api.irradiance.shade import is_surface_in_shade_series
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.azimuth import model_solar_azimuth_series
from pvgisprototype.api.position.models import (
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import (
    ABOVE_HORIZON_COLUMN_NAME,
    ALBEDO_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    BELOW_HORIZON_COLUMN_NAME,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    GLOBAL_INCLINED_IRRADIANCE,
    GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    IRRADIANCE_UNIT,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    LOW_ANGLE_COLUMN_NAME,
    MULTI_THREAD_FLAG_DEFAULT,
    PERIGEE_OFFSET,
    RADIANS,
    RADIATION_MODEL_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SHADE_COLUMN_NAME,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_DEFAULT,
    TITLE_KEY_NAME,
    TOLERANCE_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.core.arrays import create_array
from pvgisprototype.core.hashing import generate_hash


@log_function_call
def calculate_global_inclined_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: float | None = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: float | None = SURFACE_TILT_DEFAULT,
    timestamps: datetime | None = None,
    timezone: ZoneInfo | None = None,
    global_horizontal_irradiance: Path | None = None,
    direct_horizontal_irradiance: Path | None = None,
    neighbor_lookup: MethodForInexactMatches = None,
    tolerance: float | None = TOLERANCE_DEFAULT,
    mask_and_scale: bool = False,
    in_memory: bool = False,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: bool = True,
    refracted_solar_zenith: float | None = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: float | None = ALBEDO_DEFAULT,
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.jenco,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    # horizon_heights: List[float]="Array of horizon elevations.")] = None,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
):
    """Calculate the global irradiance on an inclined surface [W.m-2]

    Calculate the global irradiance on an inclined surface as the sum of the
    direct, the diffuse and the ground-reflected radiation components.
    The radiation, selectively attenuated by the atmosphere, which is not
    reflected or scattered and reaches the surface directly is the direct
    radiation. The scattered radiation that reaches the ground is the
    diffuse radiation. In addition, a smaller part of radiation is reflected
    from the ground onto the inclined surface. Only small percents of reflected
    radiation contribute to inclined surfaces, thus it is sometimes ignored.
    PVGIS, however, inherits the solutions adopted in the r.sun solar radiation
    model in which both the diffuse and reflected radiation components are
    considered.

    """
    solar_altitude_series = model_solar_altitude_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        # perigee_offset=perigee_offset,
        # eccentricity_correction_factor=eccentricity_correction_factor,
        # angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )
    solar_azimuth_series = model_solar_azimuth_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        # perigee_offset=perigee_offset,
        # eccentricity_correction_factor=eccentricity_correction_factor,
        # angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=0,
        log=log,
    )
    # Masks based on the solar altitude series
    mask_above_horizon = solar_altitude_series.value > 0
    mask_low_angle = (solar_altitude_series.value >= 0) & (
        solar_altitude_series.value < 0.04
    )  # FIXME: Is the value 0.04 in radians or degrees ?
    mask_below_horizon = solar_altitude_series.value < 0
    horizon_interval = 7.5
    horizon_heights = numpy.random.uniform(0, numpy.pi / 2,int(360 / horizon_interval))
    in_shade = is_surface_in_shade_series(
        solar_altitude_series,
        solar_azimuth_series,
        horizon_heights=horizon_heights,
        horizon_interval=horizon_interval,
        # validate_output=validate_output,
    )
    mask_not_in_shade = ~in_shade
    mask_above_horizon_not_shade = np.logical_and.reduce(
        (mask_above_horizon, mask_not_in_shade)
    )

    # Initialize arrays with zeros
    shape_of_array = (
        solar_altitude_series.value.shape
    )  # Borrow shape from solar_altitude_series
    direct_inclined_irradiance_series = create_array(
        shape_of_array, dtype=dtype, init_method="zeros", backend=array_backend
    )
    diffuse_inclined_irradiance_series = create_array(
        shape_of_array, dtype=dtype, init_method="zeros", backend=array_backend
    )
    reflected_inclined_irradiance_series = create_array(
        shape_of_array, dtype=dtype, init_method="zeros", backend=array_backend
    )

    # For very low sun angles
    direct_inclined_irradiance_series[mask_low_angle] = (
        0  # Direct radiation is negligible
    )

    # For sun below the horizon
    direct_inclined_irradiance_series[mask_below_horizon] = 0
    diffuse_inclined_irradiance_series[mask_below_horizon] = 0
    reflected_inclined_irradiance_series[mask_below_horizon] = 0

    # For sun above horizon and not in shade
    if np.any(mask_above_horizon_not_shade):
        # if given, will read from external time series
        direct_inclined_irradiance_series[mask_above_horizon_not_shade] = (
            calculate_direct_inclined_irradiance_series_pvgis(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                surface_tilt=surface_tilt,
                surface_orientation=surface_orientation,
                timestamps=timestamps,
                timezone=timezone,
                direct_horizontal_component=direct_horizontal_irradiance,  # time series, optional
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                mask_and_scale=mask_and_scale,
                in_memory=in_memory,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                apply_reflectivity_factor=apply_reflectivity_factor,
                solar_position_model=solar_position_model,
                solar_incidence_model=solar_incidence_model,
                solar_time_model=solar_time_model,
                solar_constant=solar_constant,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                angle_output_units=angle_output_units,
                dtype=dtype,
                array_backend=array_backend,
                verbose=0,  # no verbosity here by choice!
                log=log,
            ).value  # Important !
        )[mask_above_horizon_not_shade]

    # Calculate diffuse and reflected irradiance for sun above horizon
    if np.any(mask_above_horizon):
        # if given, will read from external time series
        diffuse_inclined_irradiance_series[
            mask_above_horizon
        ] = calculate_diffuse_inclined_irradiance_series(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            timestamps=timestamps,
            timezone=timezone,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            refracted_solar_zenith=refracted_solar_zenith,
            global_horizontal_component=global_horizontal_irradiance,  # time series optional
            direct_horizontal_component=direct_horizontal_irradiance,  # time series, optional
            apply_reflectivity_factor=apply_reflectivity_factor,
            solar_position_model=solar_position_model,
            solar_time_model=solar_time_model,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            angle_output_units=angle_output_units,
            neighbor_lookup=neighbor_lookup,
            dtype=dtype,
            array_backend=array_backend,
            multi_thread=multi_thread,
            verbose=0,  # no verbosity here by choice!
            log=log,
        ).value[  # Important !
            mask_above_horizon
        ]
        reflected_inclined_irradiance_series[
            mask_above_horizon
        ] = calculate_ground_reflected_inclined_irradiance_series(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            timestamps=timestamps,
            timezone=timezone,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            refracted_solar_zenith=refracted_solar_zenith,
            albedo=albedo,
            global_horizontal_component=global_horizontal_irradiance,  # time series, optional
            apply_reflectivity_factor=apply_reflectivity_factor,
            solar_position_model=solar_position_model,
            solar_time_model=solar_time_model,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            angle_output_units=angle_output_units,
            dtype=dtype,
            array_backend=array_backend,
            verbose=0,  # no verbosity here by choice!
            log=log,
        ).value[  # Important !
            mask_above_horizon
        ]

    # sum components
    global_inclined_irradiance_series = (
        direct_inclined_irradiance_series
        + diffuse_inclined_irradiance_series
        + reflected_inclined_irradiance_series
    )
    # Warning
    out_of_range_indices = np.where(
        (global_inclined_irradiance_series < LOWER_PHYSICALLY_POSSIBLE_LIMIT)
        | (global_inclined_irradiance_series > UPPER_PHYSICALLY_POSSIBLE_LIMIT)
    )
    if out_of_range_indices[0].size > 0:
        logger.warning(
            f"{WARNING_OUT_OF_RANGE_VALUES} in `global_inclined_irradiance_series` : {out_of_range_indices[0]}!"
        )

    # Building the output dictionary ========================================

    components_container = {
        "main": lambda: {
            TITLE_KEY_NAME: GLOBAL_INCLINED_IRRADIANCE,
            GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME: global_inclined_irradiance_series,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        },  # if verbose > 0 else {},
        "extended": lambda: (
            {
                TITLE_KEY_NAME: GLOBAL_INCLINED_IRRADIANCE + " & relevant components",
                SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_tilt, angle_output_units
                ),
                SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_orientation, angle_output_units
                ),
            }
            if verbose > 1
            else {}
        ),
        "more_extended": lambda: (
            {
                DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME: direct_inclined_irradiance_series,
                DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series,
                REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME: reflected_inclined_irradiance_series,
            }
            if verbose > 2
            else {}
        ),
        "even_more_extended": lambda: (
            {
                SHADE_COLUMN_NAME: in_shade,
                ABOVE_HORIZON_COLUMN_NAME: mask_above_horizon,
                LOW_ANGLE_COLUMN_NAME: mask_low_angle,
                BELOW_HORIZON_COLUMN_NAME: mask_below_horizon,
            }
            if verbose > 3
            else {}
        ),
        "fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    global_inclined_irradiance_series
                ),
            }
            if fingerprint
            else {}
        ),
    }

    components = {}
    for key, component in components_container.items():
        components.update(component())

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=global_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
        value=global_inclined_irradiance_series,
        unit=IRRADIANCE_UNIT,
        position_algorithm="",
        timing_algorithm="",
        elevation=elevation,
        surface_orientation=None,
        surface_tilt=None,
        components=components,
    )
