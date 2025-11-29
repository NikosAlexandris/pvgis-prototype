#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from pvgisprototype.log import logger
from typing import List
from zoneinfo import ZoneInfo

import numpy as np
from devtools import debug
from numpy import ndarray
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray

from pvgisprototype import (
    SolarAzimuth,
    DirectHorizontalIrradiance,
    DiffuseSkyReflectedInclinedIrradiance,
    LinkeTurbidityFactor,
    SurfaceOrientation,
    SurfaceTilt,
)
from pvgisprototype.algorithms.muneer.irradiance.diffuse.clear_sky.inclined import calculate_clear_sky_diffuse_inclined_irradiance_muneer
from pvgisprototype.algorithms.muneer.irradiance.diffuse.inclined import calculate_diffuse_inclined_irradiance_muneer
from pvgisprototype.algorithms.martin_ruiz.reflectivity import (
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
from pvgisprototype.constants import (
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LOG_LEVEL_DEFAULT,
    ECCENTRICITY_PHASE_OFFSET,
    RADIANS,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.core.arrays import create_array
from pvgisprototype.log import log_data_fingerprint, log_function_call


@log_function_call
def calculate_diffuse_inclined_irradiance(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo | None = None,
    global_horizontal_irradiance: ndarray | None = None,
    direct_horizontal_irradiance: ndarray | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(),
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    # refracted_solar_zenith: (
    #     float | None
    # ) = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    sun_horizon_position: List[SunHorizonPositionModel] = SUN_HORIZON_POSITION_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SOLAR_INCIDENCE_ALGORITHM_DEFAULT,
    # complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,  # Let Me Hardcoded, Read the docstring!
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvgis,
    shading_states: List[ShadingState] = [ShadingState.all],
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output:bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> DiffuseSkyReflectedInclinedIrradiance:
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
    # build reusable parameter dictionaries
    coordinates = {
        'longitude': longitude,
        'latitude': latitude,
    }
    time = {
        'timestamps': timestamps,
        'timezone': timezone,
    }
    solar_positioning = {
        'solar_position_model': solar_position_model,
        'adjust_for_atmospheric_refraction': adjust_for_atmospheric_refraction,
        'solar_time_model': solar_time_model,
    }
    surface_position = {
        'surface_orientation': surface_orientation,
        'surface_tilt': surface_tilt,
    }
    earth_orbit = {
        'eccentricity_phase_offset': eccentricity_phase_offset,
        'eccentricity_amplitude': eccentricity_amplitude,
    }
    array_parameters = {
        "dtype": dtype,
        "array_backend": array_backend,
    }
    output_parameters = {
        'verbose': verbose,  # Is this wanted here ? i.e. not setting = 0 ?
        'log': log,
    }

    # Some quantities are not always required, hence set them to avoid UnboundLocalError!
    extended_array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "backend": array_backend,
        "init_method": "zeros",
    }  # Borrow shape from timestamps

    solar_azimuth_series = SolarAzimuth(value=create_array(**extended_array_parameters))
    solar_incidence_series = create_array(**extended_array_parameters)

    # Calculate quantities required : ---------------------------- >>> >>> >>>
    # 1. to model the diffuse horizontal irradiance [optional]
    # 2. to calculate the diffuse sky ... to consider shaded, sunlit and potentially sunlit surfaces
    #
    # extraterrestrial on a horizontal surface requires the solar altitude
    solar_altitude_series = model_solar_altitude_series(
        **coordinates,
        **time,
        **solar_positioning,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        **earth_orbit,
        **array_parameters,
        **output_parameters,
    )
    # Calculate quantities required : ---------------------------- <<< <<< <<<

    if surface_tilt > SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD:  # tilted (or inclined) surface
        # requires the solar incidence angle for shading and times of sunlit surface
        solar_incidence_series = model_solar_incidence_series(
            **coordinates,
            **time,
            **surface_position,
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
            solar_incidence_model=solar_incidence_model,
            horizon_profile=horizon_profile,
            shading_model=shading_model,
            complementary_incidence_angle=True,  # True = between sun-vector and surface-plane !
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            **earth_orbit,
            **array_parameters,
            validate_output=validate_output,
            **output_parameters,
        )

        # Potentially sunlit surface series : solar altitude < 0.1 radians (or < 5.7 degrees)
        if np.any(solar_altitude_series.radians < 0.1):  # requires the solar azimuth
            solar_azimuth_series = model_solar_azimuth_series(
                **coordinates,
                **time,
                **solar_positioning,
                # unrefracted_solar_zenith=unrefracted_solar_zenith,
                **earth_orbit,
                verbose=verbose,
            )

    surface_in_shade_series = model_surface_in_shade_series(
        horizon_profile=horizon_profile,
        **coordinates,
        **time,
        **solar_positioning,
        shading_model=shading_model,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        **earth_orbit,
        **array_parameters,
        validate_output=validate_output,
        **output_parameters,
    )

    common_input_parameters = {
        **surface_position,
        **time,
        'global_horizontal_irradiance_series': global_horizontal_irradiance,
        'direct_horizontal_irradiance_series': direct_horizontal_irradiance,
        'apply_reflectivity_factor': apply_reflectivity_factor,
        'solar_altitude_series': solar_altitude_series,
        'solar_azimuth_series': solar_azimuth_series,
        'solar_incidence_series': solar_incidence_series,
        'surface_in_shade_series': surface_in_shade_series,
        'shading_states': shading_states,
        'solar_constant': solar_constant,
        **earth_orbit,
        **array_parameters,
        **output_parameters,
    }

    # if solar irradiance time series read from external data
    if isinstance(global_horizontal_irradiance, ndarray) and isinstance(
        direct_horizontal_irradiance, (ndarray, DirectHorizontalIrradiance)
    ):
        diffuse_inclined_irradiance_series = (
            calculate_diffuse_inclined_irradiance_muneer(
                **common_input_parameters,
            )
        )
    else:  # simulate the clear-sky index
        diffuse_inclined_irradiance_series = (
            calculate_clear_sky_diffuse_inclined_irradiance_muneer(
                elevation=elevation,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                **common_input_parameters,
            )
        )
        # ==========================================================================
        # Following do not affect calculations, yet important are they for the output !
        # Perhaps find a way to "hide" them ?
        diffuse_inclined_irradiance_series.angle_output_units = angle_output_units
        diffuse_inclined_irradiance_series.solar_altitude = getattr(
            solar_altitude_series, angle_output_units
        )
        # ==========================================================================

    diffuse_inclined_irradiance_series.reflected_percentage = (
        calculate_reflectivity_effect_percentage(
            irradiance=diffuse_inclined_irradiance_series.value_before_reflectivity,
            reflectivity=diffuse_inclined_irradiance_series.reflectivity_factor,
        )
    )
    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    diffuse_inclined_irradiance_series.build_output(verbose, fingerprint)

    log_data_fingerprint(
        data=diffuse_inclined_irradiance_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return diffuse_inclined_irradiance_series
