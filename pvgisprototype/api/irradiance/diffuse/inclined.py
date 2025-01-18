from pathlib import Path
from typing import List
from zoneinfo import ZoneInfo

import numpy as np
from devtools import debug
from numpy import ndarray
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray

from pvgisprototype import (
    Irradiance,
    LinkeTurbidityFactor,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.algorithms.pvis.diffuse.inclined import calculate_diffuse_inclined_irradiance_series_pvgis
from pvgisprototype.api.irradiance.diffuse.horizontal_from_sarah import (
    read_horizontal_irradiance_components_from_sarah,
)
from pvgisprototype.algorithms.martin_ruiz.reflectivity import (
    calculate_reflectivity_effect,
    calculate_reflectivity_effect_percentage,
)
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.azimuth import model_solar_azimuth_series
from pvgisprototype.api.position.incidence import model_solar_incidence_series
from pvgisprototype.api.position.models import (
    SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SUN_HORIZON_POSITION_DEFAULT,
    SolarIncidenceModel,
    SolarPositionModel,
    SunHorizonPositionModel,
    SolarTimeModel,
    ShadingModel,
    ShadingState,
)
from pvgisprototype.api.position.shading import model_surface_in_shade_series
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.constants import (
    ALTITUDE_COLUMN_NAME,
    ANGLE_UNITS_COLUMN_NAME,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    AZIMUTH_COLUMN_NAME,
    AZIMUTH_DIFFERENCE_COLUMN_NAME,
    AZIMUTH_ORIGIN_COLUMN_NAME,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIFFUSE_CLEAR_SKY_IRRADIANCE_COLUMN_NAME,
    DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE,
    DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
    EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    INCIDENCE_ALGORITHM_COLUMN_NAME,
    INCIDENCE_COLUMN_NAME,
    IRRADIANCE_UNIT,
    KB_RATIO_COLUMN_NAME,
    LINKE_TURBIDITY_COLUMN_NAME,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
    OUT_OF_RANGE_INDICES_COLUMN_NAME,
    PERIGEE_OFFSET,
    PERIGEE_OFFSET_COLUMN_NAME,
    POSITION_ALGORITHM_COLUMN_NAME,
    RADIANS,
    RADIATION_MODEL_COLUMN_NAME,
    REFLECTIVITY_COLUMN_NAME,
    REFLECTIVITY_FACTOR_COLUMN_NAME,
    REFLECTIVITY_PERCENTAGE_COLUMN_NAME,
    REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SHADING_STATES_COLUMN_NAME,
    SHADING_STATE_COLUMN_NAME,
    SOLAR_CONSTANT,
    SOLAR_CONSTANT_COLUMN_NAME,
    SUN_HORIZON_POSITIONS_NAME,
    SUN_HORIZON_POSITION_NAME,
    SURFACE_IN_SHADE_COLUMN_NAME,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    TERM_N_COLUMN_NAME,
    TIME_ALGORITHM_COLUMN_NAME,
    TITLE_KEY_NAME,
    UNIT_NAME,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.core.arrays import create_array
from pvgisprototype.core.hashing import generate_hash
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger


@log_function_call
def calculate_diffuse_inclined_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo | None = None,
    global_horizontal_irradiance: ndarray | str | Path | None = None,
    direct_horizontal_irradiance: ndarray | str | Path | None = None,
    # neighbor_lookup: MethodForInexactMatches | None = NEIGHBOR_LOOKUP_DEFAULT,
    # tolerance: float | None = TOLERANCE_DEFAULT,
    # mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    # in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: (
        float | None
    ) = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    sun_horizon_position: List[SunHorizonPositionModel] = SUN_HORIZON_POSITION_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    # complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,  # Let Me Hardcoded, Read the docstring!
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    shading_states: List[ShadingState] = [ShadingState.all],
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output:bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> Irradiance:
    """Calculate the diffuse irradiance incident on a solar surface.

    Notes
    -----

    In order or appearance:

    - extraterrestrial_normal_irradiance : G0
    - extraterrestrial_horizontal_irradiance : G0h = G0 sin(h0)
    - kb : Proportion between direct (beam) and extraterrestrial irradiance : Kb
    - diffuse_horizontal_component : Dhc [W.m-2]
    - diffuse_transmission_function() :
    - linke_turbidity_factor :
    - diffuse_solar_altitude_function() :
    - solar_altitude :
    - calculate_term_n():
    - n : the N term
    - diffuse_sky_irradiance()
    - sine_solar_incidence_angle
    - sine_solar_altitude
    - diffuse_sky_irradiance
    - calculate_diffuse_sky_irradiance() : F(γN)
    - surface_tilt :
    - diffuse_inclined_irradiance :
    - diffuse_horizontal_component :
    - azimuth_difference :
    - solar_azimuth :
    - surface_orientation :
    - diffuse_irradiance

    """
    # Some quantities are not always required, hence set them to avoid UnboundLocalError!
    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": "zeros",
        "backend": array_backend,
    }  # Borrow shape from timestamps
    from pvgisprototype import SolarAzimuth
    solar_azimuth_series = SolarAzimuth(value=create_array(**array_parameters))
    azimuth_difference_series = NOT_AVAILABLE
    solar_incidence_series = create_array(**array_parameters)

    # Calculate quantities required : ---------------------------- >>> >>> >>>
    # 1. to model the diffuse horizontal irradiance [optional]
    # 2. to calculate the diffuse sky ... to consider shaded, sunlit and potentially sunlit surfaces
    #
    # extraterrestrial on a horizontal surface requires the solar altitude
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
        verbose=verbose,  # Is this wanted here ? i.e. not setting = 0 ?
        log=log,
    )
    # Calculate quantities required : ---------------------------- <<< <<< <<<

    if surface_tilt > SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD:  # tilted (or inclined) surface
        # requires the solar incidence angle for shading and times of sunlit surface
        solar_incidence_series = model_solar_incidence_series(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            solar_incidence_model=solar_incidence_model,
            horizon_profile=horizon_profile,
            shading_model=shading_model,
            complementary_incidence_angle=True,  # True = between sun-vector and surface-plane !
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            validate_output=validate_output,
            verbose=verbose,
            log=log,
        )

        # Potentially sunlit surface series : solar altitude < 0.1 radians (or < 5.7 degrees)
        if np.any(solar_altitude_series.radians < 0.1):  # requires the solar azimuth
            solar_azimuth_series = model_solar_azimuth_series(
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
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        dtype=dtype,
        array_backend=array_backend,
        validate_output=validate_output,
        verbose=verbose,
        log=log,
    )
    diffuse_inclined_irradiance_series = calculate_diffuse_inclined_irradiance_series_pvgis(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            timestamps=timestamps,
            timezone=timezone,
            global_horizontal_irradiance_series=global_horizontal_irradiance,
            direct_horizontal_irradiance_series=direct_horizontal_irradiance,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            apply_reflectivity_factor=apply_reflectivity_factor,
            solar_altitude_series=solar_altitude_series,
            solar_azimuth_series=solar_azimuth_series,
            solar_incidence_series=solar_incidence_series,
            surface_in_shade_series=surface_in_shade_series,
            shading_states=shading_states,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
            )

    # Building the output dictionary ========================================

    components_container = {
        DIFFUSE_INCLINED_IRRADIANCE: lambda: {
            TITLE_KEY_NAME: DIFFUSE_INCLINED_IRRADIANCE,
            DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series.value,
            RADIATION_MODEL_COLUMN_NAME: HOFIERKA_2002,
        },  # if verbose > 0 else {},
        "Reflectivity effect": lambda: (
            {
                REFLECTIVITY_COLUMN_NAME: calculate_reflectivity_effect(
                    irradiance=diffuse_inclined_irradiance_series.before_reflectivity,
                    reflectivity=diffuse_inclined_irradiance_series.reflectivity_factor,
                ),
                REFLECTIVITY_PERCENTAGE_COLUMN_NAME: calculate_reflectivity_effect_percentage(
                    irradiance=diffuse_inclined_irradiance_series.before_reflectivity,
                    reflectivity=diffuse_inclined_irradiance_series.reflectivity_factor,
                ),
            }
            if verbose > 6 and apply_reflectivity_factor
            else {}
        ),
        "Reflectivity factor": lambda: (
            {
                # REFLECTIVITY_FACTOR_COLUMN_NAME: where(diffuse_irradiance_loss_factor_series <= 0, 0, (1 - diffuse_irradiance_loss_factor_series)),
                REFLECTIVITY_FACTOR_COLUMN_NAME: diffuse_inclined_irradiance_series.reflectivity_factor,
                DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: diffuse_inclined_irradiance_series.before_reflectivity,
                # } if verbose > 1 and apply_reflectivity_factor else {},
            }
            if apply_reflectivity_factor
            else {}
        ),
        "Diffuse Solar Altitude Metadata": lambda: (
            {
                TERM_N_COLUMN_NAME: diffuse_inclined_irradiance_series.term_n,
                KB_RATIO_COLUMN_NAME: diffuse_inclined_irradiance_series.kb_ratio,
                AZIMUTH_DIFFERENCE_COLUMN_NAME: getattr(
                    azimuth_difference_series, angle_output_units, np.nan
                ),
            }
            if verbose > 3
            else {}
        ),
        "Irradiance Metadata": lambda: (
            {
                GLOBAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series.global_horizontal_irradiance,
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series.direct_horizontal_irradiance,
                EXTRATERRESTRIAL_HORIZONTAL_IRRADIANCE_COLUMN_NAME:diffuse_inclined_irradiance_series.extraterrestrial_horizontal_irradiance,
                EXTRATERRESTRIAL_NORMAL_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series.extraterrestrial_normal_irradiance,
                LINKE_TURBIDITY_COLUMN_NAME: linke_turbidity_factor_series.value,
            }
            if verbose > 4
            else {}
        ),
        "Solar incidence": lambda: (
            {
                SHADING_STATES_COLUMN_NAME: diffuse_inclined_irradiance_series.shading_states,
                SHADING_STATE_COLUMN_NAME: diffuse_inclined_irradiance_series.shading_state_series,
            }
            if verbose > 5
            else {}
        ),
        "Surface position": lambda: (
            {
                SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_orientation, angle_output_units
                ),
                SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(
                    surface_tilt, angle_output_units
                ),
                SURFACE_IN_SHADE_COLUMN_NAME: surface_in_shade_series.value,
                TITLE_KEY_NAME: DIFFUSE_INCLINED_IRRADIANCE + " & relevant components",
                DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series.diffuse_horizontal_irradiance,
                DIFFUSE_CLEAR_SKY_IRRADIANCE_COLUMN_NAME: diffuse_inclined_irradiance_series.diffuse_sky_irradiance,
            }
            if verbose > 2
            else {}
        ),
        "Solar position": lambda: {
            INCIDENCE_COLUMN_NAME: (
                getattr(solar_incidence_series, angle_output_units, NOT_AVAILABLE)
                if solar_incidence_series is not None
                else None
            ),
            ALTITUDE_COLUMN_NAME: (
                getattr(solar_altitude_series, angle_output_units)
                if solar_altitude_series
                else None
            ),  # Altitude should be always there! If not, something is wrong.  This is why this entry does not need the NOT_AVAILABLE fallback.
            AZIMUTH_COLUMN_NAME: getattr(
                solar_azimuth_series, angle_output_units, NOT_AVAILABLE
            ),
            # SUN_HORIZON_POSITION_COLUMN_NAME: sun_horizon_position_series,
        }
        if verbose > 9
        else {},
        "Solar Position Metadata": lambda: {
            UNIT_NAME: angle_output_units,
            INCIDENCE_ALGORITHM_COLUMN_NAME: solar_incidence_model,
            # SUN_HORIZON_POSITIONS_NAME: sun_horizon_positions,
            AZIMUTH_ORIGIN_COLUMN_NAME: getattr(solar_azimuth_series, 'origin'),
            POSITION_ALGORITHM_COLUMN_NAME: solar_altitude_series.position_algorithm,
            TIME_ALGORITHM_COLUMN_NAME: solar_altitude_series.timing_algorithm,
            SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            PERIGEE_OFFSET_COLUMN_NAME: perigee_offset,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_correction_factor,
        },
        "Out-of-range": lambda: (
            {
                OUT_OF_RANGE_INDICES_COLUMN_NAME: diffuse_inclined_irradiance_series.out_of_range,
                OUT_OF_RANGE_INDICES_COLUMN_NAME + " i": diffuse_inclined_irradiance_series.out_of_range_index,
            }
            if diffuse_inclined_irradiance_series.out_of_range.any() > 0
            else {}
        ),
        "Fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    diffuse_inclined_irradiance_series.value
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
        data=diffuse_inclined_irradiance_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return Irradiance(
        value=diffuse_inclined_irradiance_series.value,
        unit=IRRADIANCE_UNIT,
        position_algorithm=solar_altitude_series.position_algorithm,
        timing_algorithm=solar_altitude_series.timing_algorithm,
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        components=components,
    )
