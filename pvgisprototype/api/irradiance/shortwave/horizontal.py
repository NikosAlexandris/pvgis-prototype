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

from datetime import datetime
from zoneinfo import ZoneInfo

from devtools import debug
from xarray import DataArray

from pvgisprototype import GlobalHorizontalIrradiance, LinkeTurbidityFactor
from pvgisprototype.api.irradiance.diffuse.clear_sky.horizontal import calculate_clear_sky_diffuse_horizontal_irradiance
from pvgisprototype.api.irradiance.direct.horizontal import (
    calculate_clear_sky_direct_horizontal_irradiance_series,
)
from pvgisprototype.api.position.models import ShadingModel, SolarPositionModel, SolarTimeModel
from pvgisprototype.constants import (
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    LOG_LEVEL_DEFAULT,
    ECCENTRICITY_PHASE_OFFSET,
    RADIANS,
    UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SOLAR_CONSTANT,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
def calculate_global_horizontal_irradiance_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: datetime | None = None,
    timezone: ZoneInfo | None = None,
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(),
    adjust_for_atmospheric_refraction: bool = True,
    # unrefracted_solar_zenith: UnrefractedSolarZenith | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvgis,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
):
    """
    Calculate the clear-sky global horizontal irradiance (GHI)

    The global horizontal irradiance represents the total amount of shortwave
    radiation received from above by a surface horizontal to the ground. It
    includes both the direct and the diffuse solar radiation.

    """
    if verbose > 0:
        logger.debug(
            ":information: Modelling direct horizontal irradiance...",
            alt=":information: [bold][magenta]Modelling[/magenta] direct horizontal irradiance[/bold]...",
        )
    direct_horizontal_irradiance_series = calculate_clear_sky_direct_horizontal_irradiance_series(
        longitude=longitude,  # required by some of the solar time algorithms
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        timezone=timezone,
        solar_time_model=solar_time_model,
        solar_position_model=solar_position_model,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
        # unrefracted_solar_zenith=unrefracted_solar_zenith,
        solar_constant=solar_constant,
        eccentricity_phase_offset=eccentricity_phase_offset,
        eccentricity_amplitude=eccentricity_amplitude,
        horizon_profile=horizon_profile,
        shading_model=shading_model,
        # angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        validate_output=validate_output,
        verbose=verbose,
        log=log,
        fingerprint=fingerprint,
    )
    diffuse_horizontal_irradiance_series = (
        calculate_clear_sky_diffuse_horizontal_irradiance(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            timezone=timezone,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
            # unrefracted_solar_zenith=unrefracted_solar_zenith,
            solar_position_model=solar_position_model,
            solar_time_model=solar_time_model,
            solar_constant=solar_constant,
            eccentricity_phase_offset=eccentricity_phase_offset,
            eccentricity_amplitude=eccentricity_amplitude,
            # angle_output_units=angle_output_units,
            dtype=dtype,
            array_backend=array_backend,
            verbose=verbose,
            log=log,
            fingerprint=fingerprint,
        )
    )
    global_horizontal_irradiance_series = (
        direct_horizontal_irradiance_series.value
        + diffuse_horizontal_irradiance_series.value
    )

    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=global_horizontal_irradiance_series,
        shape=timestamps.shape,
        data_model=GlobalHorizontalIrradiance(),
    )

    global_horizontal_irradiance_series = GlobalHorizontalIrradiance(
        value=global_horizontal_irradiance_series,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        direct_horizontal_irradiance=direct_horizontal_irradiance_series,
        extraterrestrial_normal_irradiance=diffuse_horizontal_irradiance_series.extraterrestrial_normal_irradiance,
        linke_turbidity_factor=linke_turbidity_factor_series,
        # value_before_reflectivity=diffuse_inclined_irradiance_before_reflectivity_series if diffuse_inclined_irradiance_before_reflectivity_series is not None else NOT_AVAILABLE,
        # reflectivity_factor= diffuse_irradiance_reflectivity_factor_series if diffuse_inclined_irradiance_before_reflectivity_series is not None else NOT_AVAILABLE,
        # surface_in_shade=direct_horizontal_irradiance_series.surface_in_shade, ###  We Need This !
        # shading_states=shading_states,
        # shading_state=shading_state_series,
        diffuse_horizontal_irradiance=diffuse_horizontal_irradiance_series,
        # diffuse_sky_irradiance=diffuse_sky_irradiance_series,
        # term_n=n_series,
        # kb_ratio=kb_series,
        solar_positioning_algorithm=direct_horizontal_irradiance_series.solar_altitude.solar_positioning_algorithm,
        solar_timing_algorithm=direct_horizontal_irradiance_series.solar_altitude.solar_timing_algorithm,
        # shading_algorithm=shading_model,
        elevation=elevation,
        # surface_orientation=surface_orientation,
        # surface_tilt=surface_tilt,
        solar_altitude=direct_horizontal_irradiance_series.solar_altitude,
        # solar_azimuth=direct_horizontal_irradiance_series.solar_azimuth,
        # azimuth_difference=azimuth_difference_series,
        adjusted_for_atmospheric_refraction=direct_horizontal_irradiance_series.solar_altitude.adjusted_for_atmospheric_refraction,
        # solar_incidence=solar_incidence_series,
        # solar_incidence_model=solar_incidence_series.incidence_algorithm,
        # solar_incidence_definition=solar_incidence_series.definition,
        solar_radiation_model=HOFIERKA_2002,
        data_source=HOFIERKA_2002,
    )

    # ==========================================================================
    # Following do not affect calculations, yet important are they for the output !
    # Perhaps find a way to "hide" them ?
    global_horizontal_irradiance_series.angle_output_units = angle_output_units
    # global_horizontal_irradiance_series.solar_altitude = getattr(
    #     solar_altitude_series, angle_output_units
    # )
    # global_horizontal_irradiance_series.adjusted_for_atmospheric_refraction = (
    #     solar_altitude_series.adjusted_for_atmospheric_refraction
    # )
    # ==========================================================================

    global_horizontal_irradiance_series.build_output(verbose, fingerprint)

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=global_horizontal_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    return global_horizontal_irradiance_series
