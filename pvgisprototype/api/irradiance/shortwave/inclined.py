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
"""
API module to calculate the global (shortwave) irradiance over a
location for a period in time.
"""

from typing import List
from zoneinfo import ZoneInfo

import numpy
from devtools import debug
from numpy._core.multiarray import ndarray
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray

from pvgisprototype import LinkeTurbidityFactor
# from pvgisprototype.api.irradiance.shade import is_surface_in_shade_series
from pvgisprototype.api.position.azimuth import model_solar_azimuth_series
from pvgisprototype.api.position.incidence import model_solar_incidence_series
from pvgisprototype import (
    SolarAzimuth,
    SurfaceOrientation,
    SurfaceTilt,
    LinkeTurbidityFactor,
    GlobalInclinedIrradiance,
)
from pvgisprototype.api.surface.parameters import (
    build_location_dictionary,
)
from pvgisprototype.api.position.altitude import model_solar_altitude_series
from pvgisprototype.api.position.models import (
    SUN_HORIZON_POSITION_DEFAULT,
    ShadingState,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
    ShadingModel,
    SunHorizonPositionModel,
)
from pvgisprototype.api.position.shading import model_surface_in_shade_series
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    ECCENTRICITY_PHASE_OFFSET,
    # UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_DEFAULT,
    SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array
from typing import List
from zoneinfo import ZoneInfo

import numpy
from devtools import debug
from numpy._core.multiarray import ndarray
from pandas import DatetimeIndex, Timestamp
from xarray import DataArray
from pandas import DatetimeIndex, Timestamp
from pvgisprototype.algorithms.hofierka.irradiance.shortwave.clear_sky.inclined import calculate_clear_sky_global_inclined_irradiance_hofierka
from pvgisprototype.algorithms.hofierka.irradiance.shortwave.inclined import calculate_global_inclined_irradiance_hofierka


@log_function_call
def calculate_global_inclined_irradiance(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: SurfaceOrientation = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTilt = SURFACE_TILT_DEFAULT,
    surface_tilt_horizontally_flat_panel_threshold: float = SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    timestamps: DatetimeIndex = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo | None = ZoneInfo("UTC"),
    global_horizontal_irradiance: ndarray | None = None,
    direct_horizontal_irradiance: ndarray | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    adjust_for_atmospheric_refraction: bool = True,
    # unrefracted_solar_zenith: UnrefractedSolarZenith | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: float | None = ALBEDO_DEFAULT,
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    sun_horizon_position: List[SunHorizonPositionModel] = SUN_HORIZON_POSITION_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.jenco,
    # complementary_incidence_angle: bool = COMPLEMENTARY_INCIDENCE_ANGLE_DEFAULT,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    shading_states: List[ShadingState] = [ShadingState.all],
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    # angle_output_units: str = RADIANS,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
) -> GlobalInclinedIrradiance:
    """
    """
    # build reusable parameter dictionaries
    coordinates = {
        'longitude': longitude,
        'latitude': latitude,
    }
    location_arguments = build_location_dictionary(
        **coordinates,
        elevation=elevation,
    )
    time = {
        'timestamps': timestamps,
        'timezone': timezone,
    }
    horizontal_irradiance = {
        'global_horizontal_irradiance': global_horizontal_irradiance,
        'direct_horizontal_irradiance': direct_horizontal_irradiance,
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
        "init_method": "empty",
        "backend": array_backend,
    }  # Borrow shape from timestamps
    solar_azimuth_series = SolarAzimuth(
            value=create_array(**extended_array_parameters),
            origin='Not Required!',
            )
    solar_incidence_series = model_solar_incidence_series(
            **coordinates,
            **time,
            **surface_position,
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
            solar_time_model=solar_time_model,
            solar_position_model=solar_position_model,
            sun_horizon_position=sun_horizon_position,
            solar_incidence_model=solar_incidence_model,
            horizon_profile=horizon_profile,
            shading_model=shading_model,
            # complementary_incidence_angle=complementary_incidence_angle,
            zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
            dtype=dtype,
            array_backend=array_backend,
            validate_output=validate_output,
            verbose=verbose,
            log=log,
        # solar_incidence_model=solar_incidence_model,
        # complementary_incidence_angle=True,  # = Sun-vector To Surface-plane (Jenčo, 1992) !
        # zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
        # **earth_orbit,
        # **array_parameters,
        # **output_parameters,
    )
    # Calculate quantities required : ---------------------------- >>> >>> >>>
    # 1. to model the diffuse horizontal irradiance [optional]
    # 2. to calculate the diffuse sky ... to consider shaded, sunlit and potentially sunlit surfaces
    
    # extraterrestrial on a horizontal surface requires the solar altitude
    solar_altitude_series = model_solar_altitude_series(
        **coordinates,
        **time,
        solar_position_model=solar_position_model,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        # solar_time_model=solar_time_model,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        # angle_output_units=angle_output_units,
        **array_parameters,
        validate_output=validate_output,
        **output_parameters,
    )
    # Calculate quantities required : ---------------------------- <<< <<< <<<

    if surface_tilt > surface_tilt_horizontally_flat_panel_threshold:  # tilted (or inclined) surface
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
        if numpy.any(solar_altitude_series.radians < 0.1):  # requires the solar azimuth
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
    if isinstance(global_horizontal_irradiance, ndarray) and isinstance(
        direct_horizontal_irradiance, ndarray
    ):
        global_inclined_irradiance_series = calculate_global_inclined_irradiance_hofierka(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            timestamps=timestamps,
            timezone=timezone,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            **horizontal_irradiance,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            # unrefracted_solar_zenith=unrefracted_solar_zenith,
            albedo=albedo,
            apply_reflectivity_factor=apply_reflectivity_factor,
            solar_incidence_series=solar_incidence_series,
            solar_altitude_series=solar_altitude_series,
            solar_azimuth_series=solar_azimuth_series,
            **solar_positioning,
            sun_horizon_position=sun_horizon_position,
            surface_in_shade_series=surface_in_shade_series,
            shading_states=shading_states,
            # solar_incidence_model=solar_incidence_model,
            # zero_negative_solar_incidence_angle=zero_negative_solar_incidence_angle,
            # horizon_profile=horizon_profile,
            # shading_model=shading_model,
            solar_constant=solar_constant,
            **earth_orbit,
            **array_parameters,
            validate_output=validate_output,
            **output_parameters,
            # angle_output_units=angle_output_units,
            fingerprint=fingerprint,
        )
    else:
        global_inclined_irradiance_series = calculate_clear_sky_global_inclined_irradiance_hofierka(
            **location_arguments,
            **surface_position,
            surface_tilt_horizontally_flat_panel_threshold=surface_tilt_horizontally_flat_panel_threshold,
            **time,
            **horizontal_irradiance,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            # unrefracted_solar_zenith=unrefracted_solar_zenith,
            albedo=albedo,
            apply_reflectivity_factor=apply_reflectivity_factor,
            solar_incidence_series=solar_incidence_series,
            solar_altitude_series=solar_altitude_series,
            solar_azimuth_series=solar_azimuth_series,
            **solar_positioning,
            sun_horizon_position=sun_horizon_position,
            surface_in_shade_series=surface_in_shade_series,
            shading_states=shading_states,
            solar_constant=solar_constant,
            **earth_orbit,
            **array_parameters,
            validate_output=validate_output,
            **output_parameters,
            # angle_output_units=angle_output_units,
            fingerprint=fingerprint,
        )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    global_inclined_irradiance_series.build_output(verbose, fingerprint)

    log_data_fingerprint(
        data=global_inclined_irradiance_series.value,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return global_inclined_irradiance_series
