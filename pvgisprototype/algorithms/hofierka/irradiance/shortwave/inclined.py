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
from pydantic_numpy import NpNDArray

from pvgisprototype import (
        SolarIncidence,
        SolarAltitude,
        SolarAzimuth,
        LinkeTurbidityFactor,
        ExtraterrestrialNormalIrradiance,
        ExtraterrestrialHorizontalIrradiance,
        DirectNormalIrradiance,
        DirectHorizontalIrradianceFromExternalData,
        DirectInclinedIrradiance,
        DiffuseSkyReflectedHorizontalIrradianceFromExternalData,
        DiffuseSkyReflectedInclinedIrradiance,
        DiffuseGroundReflectedInclinedIrradiance,
        GlobalInclinedIrradianceFromExternalData,
        )
from pvgisprototype.algorithms.muneer.irradiance.diffuse.inclined import calculate_diffuse_inclined_irradiance_muneer
from pvgisprototype.algorithms.hofierka.irradiance.direct.inclined import calculate_direct_inclined_irradiance_hofierka
from pvgisprototype.api.irradiance.diffuse.ground_reflected import (
    calculate_ground_reflected_inclined_irradiance_series,
)
from pvgisprototype.api.position.models import (
    SUN_HORIZON_POSITION_DEFAULT,
    ShadingState,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
    ShadingModel,
    SunHorizonPositionModel,
    select_models,
)
from pvgisprototype.constants import (
    ALBEDO_DEFAULT,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    ECCENTRICITY_CORRECTION_FACTOR,
    FINGERPRINT_FLAG_DEFAULT,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    HOFIERKA_2002,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    NOT_AVAILABLE,
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
from pvgisprototype.core.caching import custom_cached
from pvgisprototype.log import log_data_fingerprint, log_function_call, logger
from pvgisprototype.core.arrays import create_array
from pvgisprototype.validation.models import SurfaceOrientationModel, SurfaceTiltModel
from pvgisprototype.validation.values import identify_values_out_of_range


@log_function_call
@custom_cached
def calculate_global_inclined_irradiance_hofierka(
    longitude: float,
    latitude: float,
    elevation: float,
    surface_orientation: SurfaceOrientationModel = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: SurfaceTiltModel = SURFACE_TILT_DEFAULT,
    surface_tilt_horizontally_flat_panel_threshold: float = SURFACE_TILT_HORIZONTALLY_FLAT_PANEL_THRESHOLD,
    timestamps: DatetimeIndex = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo | None = ZoneInfo("UTC"),
    global_horizontal_irradiance: ndarray = numpy.array([], dtype=DATA_TYPE_DEFAULT),
    direct_horizontal_irradiance: ndarray = numpy.array([], dtype=DATA_TYPE_DEFAULT), 
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    adjust_for_atmospheric_refraction: bool = True,
    # unrefracted_solar_zenith: UnrefractedSolarZenith | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,  # radians
    albedo: float | None = ALBEDO_DEFAULT,
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_altitude_series: SolarAltitude | None = None,
    solar_azimuth_series: SolarAzimuth | None = None,
    solar_incidence_series: SolarIncidence | None = None,
    solar_position_model: SolarPositionModel = SolarPositionModel.noaa,
    surface_in_shade_series: NpNDArray | None = None,
    sun_horizon_position: List[SunHorizonPositionModel] = SUN_HORIZON_POSITION_DEFAULT,
    shading_states: List[ShadingState] = [ShadingState.all],
    solar_time_model: SolarTimeModel = SolarTimeModel.noaa,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    validate_output:bool = VALIDATE_OUTPUT_DEFAULT,
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

    # In order to avoid unbound errors we pre-define `_series` objects
    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": "zeros",
        "backend": array_backend,
    }  # Borrow shape from timestamps
    zero_array = create_array(**array_parameters)
    extended_array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "backend": array_backend,
    }
    unset_series = create_array(**extended_array_parameters, init_method="unset")

    # # direct
    # # ----------------------------------------------- Important !
    # if direct_horizontal_irradiance is None:
    #     direct_horizontal_irradiance = zero_array
    # # Important ! -----------------------------------------------

    direct_inclined_irradiance_series = DirectInclinedIrradiance(
        value=zero_array,
        solar_incidence=SolarIncidence(value=unset_series),
    )
    direct_inclined_irradiance_series.reflected = zero_array
    direct_inclined_irradiance_series.value_before_reflectivity = zero_array
    direct_inclined_irradiance_series.reflectivity_factor = zero_array
    direct_normal_irradiance = DirectNormalIrradiance(
        value=zero_array,
        # extraterrestrial_normal_irradiance=extraterrestrial_normal_irradiance,
    )
    direct_inclined_irradiance_series.direct_horizontal_irradiance = (
        DirectHorizontalIrradianceFromExternalData(
            value=direct_horizontal_irradiance,
            direct_normal_irradiance=direct_normal_irradiance,
        )
    )
    # direct_inclined_irradiance_series.solar_incidence_model = solar_incidence_model
    # # direct_inclined_irradiance_series.solar_incidence.definition = 

    no_earth_orbit = {
        'eccentricity_phase_offset': None,
        'eccentricity_amplitude': None,
    }
    # extraterrestrial normal to be fed indirectly to diffuse_inclined_irradiance
    extraterrestrial_normal_irradiance_series = ExtraterrestrialNormalIrradiance(
        value=unset_series,
        unit=NOT_AVAILABLE,
        day_angle=unset_series,
        solar_constant=None,
        **no_earth_orbit,
        distance_correction_factor=None,
    )
    extraterrestrial_horizontal_irradiance_series = ExtraterrestrialHorizontalIrradiance(
        value=unset_series,
        unit=NOT_AVAILABLE,
        day_angle=unset_series,
        solar_constant=None,
        **no_earth_orbit,
        distance_correction_factor=None,
    )

    # diffuse sky-reflected
    diffuse_inclined_irradiance_series = DiffuseSkyReflectedInclinedIrradiance(
        value=zero_array,
        extraterrestrial_normal_irradiance=extraterrestrial_normal_irradiance_series,
        extraterrestrial_horizontal_irradiance=extraterrestrial_horizontal_irradiance_series,
        solar_azimuth=SolarAzimuth(value=unset_series),
        # direct_horizontal_irradiance=direct_horizontal_irradiance,
    )
    diffuse_inclined_irradiance_series.reflected = zero_array
    diffuse_inclined_irradiance_series.value_before_reflectivity = zero_array
    diffuse_inclined_irradiance_series.reflectivity_factor = zero_array
    diffuse_inclined_irradiance_series.diffuse_horizontal_irradiance = DiffuseSkyReflectedHorizontalIrradianceFromExternalData(value=zero_array)

    # diffuse ground-reflected
    # note : there is no ground-reflected _horizontal_ component as such !
    ground_reflected_inclined_irradiance_series = DiffuseGroundReflectedInclinedIrradiance(
        value=zero_array
    )
    ground_reflected_inclined_irradiance_series.reflected = zero_array
    ground_reflected_inclined_irradiance_series.value_before_reflectivity = zero_array
    ground_reflected_inclined_irradiance_series.reflectivity_factor = zero_array
    global_inclined_irradiance_series = zero_array

    # Select which solar positions related to the horizon to process
    sun_horizon_positions = select_models(
        SunHorizonPositionModel, sun_horizon_position
    )  # Using a Typer callback fails !
    # and keep track of the position of the sun relative to the horizon
    sun_horizon_position_series = create_array(
        timestamps.shape, dtype="object", init_method="empty", backend=array_backend
    )
    # Following, create masks based on the solar altitude series --------

    # For sun below the horizon
    if SunHorizonPositionModel.below in sun_horizon_positions:
        mask_below_horizon = solar_altitude_series.value < 0
        sun_horizon_position_series[mask_below_horizon] = [SunHorizonPositionModel.below.value]
        if numpy.any(mask_below_horizon):
            logger.info(
                f"Positions of the sun below horizon :\n{sun_horizon_position_series}",
                alt=f"Positions of the sun [bold gray50]below horizon[/bold gray50] :\n{sun_horizon_position_series}"
            )
            # no incident radiance without direct sunlight !
            direct_inclined_irradiance_series.value[mask_below_horizon] = 0
            diffuse_inclined_irradiance_series.value[mask_below_horizon] = 0
            ground_reflected_inclined_irradiance_series.value[mask_below_horizon] = 0

    # For very low sun angles
    if SunHorizonPositionModel.low_angle in sun_horizon_positions:
        mask_low_angle = numpy.logical_and(
            solar_altitude_series.value >= 0,
            solar_altitude_series.value < 0.04,  # FIXME: Is 0.04 in radians or degrees ?
            sun_horizon_position_series == None,  # operate only on unset elements
        )
        sun_horizon_position_series[mask_low_angle] = [
            SunHorizonPositionModel.low_angle.value
        ]
        direct_inclined_irradiance_series.value[mask_low_angle] = (
            0  # Direct radiation is negligible
        )

    # For sun above the horizon
    if SunHorizonPositionModel.above in sun_horizon_positions:
        mask_above_horizon = numpy.logical_and(
            solar_altitude_series.value > 0,
            sun_horizon_position_series == None,  # operate only on unset elements
        )
        sun_horizon_position_series[mask_above_horizon] = [
            SunHorizonPositionModel.above.value
        ]

        # For sun above horizon and not in shade
        mask_not_in_shade = ~surface_in_shade_series.value
        mask_above_horizon_not_in_shade = numpy.logical_and(
            mask_above_horizon,
            mask_not_in_shade,
            sun_horizon_position_series == None,
        )

        if numpy.any(mask_above_horizon_not_in_shade):
            # sun_horizon_position_series[mask_above_horizon_not_in_shade] = [SunHorizonPositionModel.above.name]
            logger.info(
                f"Including positions of the sun above horizon and not in shade :\n{sun_horizon_position_series}",
                alt=f"Including positions of the sun [bold yellow]above horizon[/bold yellow] and [bold red]not in shade[/bold red] :\n{sun_horizon_position_series}"
            )
            if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
                logger.info(
                    "i Calculating the direct inclined irradiance for moments not in shade ..",
                    alt="i [bold]Calculating[/bold] the [magenta]direct inclined irradiance[/magenta] for moments not in shade .."
                )
            # if not read from external time series,
            # will calculate the clear-sky index !
            direct_inclined_irradiance_series = calculate_direct_inclined_irradiance_hofierka(
                timestamps=timestamps,
                timezone=timezone,
                direct_horizontal_irradiance=direct_horizontal_irradiance,
                apply_reflectivity_factor=apply_reflectivity_factor,
                solar_incidence_series=solar_incidence_series,
                solar_altitude_series=solar_altitude_series,
                # solar_azimuth_series=solar_azimuth_series,
                surface_in_shade_series=surface_in_shade_series,
                dtype=dtype,
                array_backend=array_backend,
                validate_output=validate_output,
                verbose=verbose,
                log=log,
            )
            direct_inclined_irradiance_series.build_output(
                verbose=verbose, fingerprint=fingerprint
            )

        # Calculate diffuse and reflected irradiance for sun above horizon
        if not numpy.any(mask_above_horizon):
            logger.info(
                "i [yellow bold]Apparently there is no moment of the sun above the horizon in the requested time series![/yellow bold] "
            )
        else:
            if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
                logger.info(
                    "i [bold]Calculating[/bold] the [magenta]diffuse inclined irradiance[/magenta] for daylight moments .."
                )
            diffuse_inclined_irradiance_series = (
                calculate_diffuse_inclined_irradiance_muneer(
                    surface_orientation=surface_orientation,
                    surface_tilt=surface_tilt,
                    surface_tilt_horizontally_flat_panel_threshold=surface_tilt_horizontally_flat_panel_threshold,
                    timestamps=timestamps,
                    timezone=timezone,
                    global_horizontal_irradiance_series=global_horizontal_irradiance,
                    direct_horizontal_irradiance_series=direct_horizontal_irradiance,
                    apply_reflectivity_factor=apply_reflectivity_factor,
                    solar_altitude_series=solar_altitude_series,
                    solar_azimuth_series=solar_azimuth_series,
                    solar_incidence_series=solar_incidence_series,
                    surface_in_shade_series=surface_in_shade_series,
                    shading_states=shading_states,
                    solar_constant=solar_constant,
                    eccentricity_phase_offset=eccentricity_phase_offset,
                    eccentricity_amplitude=eccentricity_amplitude,
                    dtype=dtype,
                    array_backend=array_backend,
                    verbose=verbose,
                    log=log,
                )
            )
            if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
                logger.info(
                    "i [bold]Calculating[/bold] the [magenta]reflected inclined irradiance[/magenta] for daylight moments .."
                )
            ground_reflected_inclined_irradiance_series = calculate_ground_reflected_inclined_irradiance_series(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                surface_orientation=surface_orientation,
                surface_tilt=surface_tilt,
                timestamps=timestamps,
                timezone=timezone,
                global_horizontal_irradiance=global_horizontal_irradiance,  # time series, optional
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                adjust_for_atmospheric_refraction=adjust_for_atmospheric_refraction,
                # unrefracted_solar_zenith=unrefracted_solar_zenith,
                albedo=albedo,
                apply_reflectivity_factor=apply_reflectivity_factor,
                solar_position_model=solar_position_model,
                solar_time_model=solar_time_model,
                solar_constant=solar_constant,
                eccentricity_phase_offset=eccentricity_phase_offset,
                eccentricity_amplitude=eccentricity_amplitude,
                dtype=dtype,
                array_backend=array_backend,
                verbose=verbose,
                log=log,
                fingerprint=fingerprint,
            )

    # sum components
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(
            "\ni [bold]Calculating[/bold] the [magenta]global inclined irradiance[/magenta] .."
        )
    global_inclined_irradiance_series[mask_above_horizon_not_in_shade] += (
        direct_inclined_irradiance_series.value[mask_above_horizon_not_in_shade]
    )
    global_inclined_irradiance_series[mask_above_horizon] += (
        + diffuse_inclined_irradiance_series.value[mask_above_horizon]
        + ground_reflected_inclined_irradiance_series.value[mask_above_horizon]
    )
    global_inclined_reflected_series = (
        direct_inclined_irradiance_series.reflected
        + diffuse_inclined_irradiance_series.reflected
        + ground_reflected_inclined_irradiance_series.reflected
    )
    global_inclined_irradiance_before_reflectivity_series = (
        direct_inclined_irradiance_series.value_before_reflectivity
        + diffuse_inclined_irradiance_series.value_before_reflectivity
        + ground_reflected_inclined_irradiance_series.value_before_reflectivity
    )
    out_of_range, out_of_range_index = identify_values_out_of_range(
        series=global_inclined_irradiance_series,
        shape=timestamps.shape,
        data_model=GlobalInclinedIrradianceFromExternalData(),
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    log_data_fingerprint(
        data=global_inclined_irradiance_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    # We need to build this for the returned data model !
    diffuse_inclined_irradiance_series.build_output(
        verbose=verbose, fingerprint=fingerprint
    )

    return GlobalInclinedIrradianceFromExternalData(
        value=global_inclined_irradiance_series,
        out_of_range=out_of_range,
        out_of_range_index=out_of_range_index,
        #
        ## Inclined Irradiance Components
        direct_inclined_irradiance=direct_inclined_irradiance_series.value,
        diffuse_inclined_irradiance=diffuse_inclined_irradiance_series.value,
        ground_reflected_inclined_irradiance=ground_reflected_inclined_irradiance_series.value,
        #
        ## Loss due to Reflectivity
        reflected=global_inclined_reflected_series,
        direct_inclined_reflected=direct_inclined_irradiance_series.reflected,
        diffuse_inclined_reflected=diffuse_inclined_irradiance_series.reflected,
        ground_reflected_inclined_reflected=ground_reflected_inclined_irradiance_series.reflected,
        #
        ## Reflectivity Factor for Irradiance Components
        direct_inclined_reflectivity_factor=direct_inclined_irradiance_series.reflectivity_factor,
        diffuse_inclined_reflectivity_factor=diffuse_inclined_irradiance_series.reflectivity_factor,
        ground_reflected_inclined_reflectivity_factor=ground_reflected_inclined_irradiance_series.reflectivity_factor,
        #
        ## Reflectivity Coefficient which defines the Reflectivity Factor for Irradiance Components
        # direct_inclined_reflectivity_coefficient=direct_inclined_reflectivity_coefficient_series,
        diffuse_inclined_reflectivity_coefficient=diffuse_inclined_irradiance_series.reflectivity_coefficient,
        # ground_reflected_inclined_reflectivity_coefficient=ground_reflected_inclined_reflectivity_coefficient_series,
        #
        ## Inclined Irradiance before loss due to Reflectivity
        value_before_reflectivity=global_inclined_irradiance_before_reflectivity_series,
        direct_inclined_before_reflectivity=direct_inclined_irradiance_series.value_before_reflectivity,
        diffuse_inclined_before_reflectivity=diffuse_inclined_irradiance_series.value_before_reflectivity,
        ground_reflected_inclined_before_reflectivity=ground_reflected_inclined_irradiance_series.value_before_reflectivity,
        #
        ## Horizontal Irradiance Components
        global_horizontal_irradiance=global_horizontal_irradiance,
        direct_horizontal_irradiance=direct_inclined_irradiance_series.direct_horizontal_irradiance,
        diffuse_horizontal_irradiance=diffuse_inclined_irradiance_series.diffuse_horizontal_irradiance,
        #
        ## Components of the diffuse sky-reflected irradiance
        diffuse_sky_irradiance=diffuse_inclined_irradiance_series.diffuse_sky_irradiance,
        term_n=diffuse_inclined_irradiance_series.term_n,
        kb_ratio=diffuse_inclined_irradiance_series.kb_ratio,
        #
        ## Components of the Extraterrestrial irradiance
        extraterrestrial_horizontal_irradiance=diffuse_inclined_irradiance_series.extraterrestrial_horizontal_irradiance,
        extraterrestrial_normal_irradiance=diffuse_inclined_irradiance_series.extraterrestrial_normal_irradiance,
        linke_turbidity_factor=linke_turbidity_factor_series,
        #
        ## Location and Position
        elevation=elevation,
        surface_orientation=surface_orientation,
        surface_tilt=surface_tilt,
        sun_horizon_positions=sun_horizon_positions,  # states != sun_horizon_position
        #
        ## Solar Position parameters
        surface_in_shade=surface_in_shade_series,
        solar_incidence=direct_inclined_irradiance_series.solar_incidence,
        shading_state=diffuse_inclined_irradiance_series.shading_state,
        sun_horizon_position=sun_horizon_position_series,  # positions != sun_horizon_positions
        solar_altitude=solar_altitude_series,
        refracted_solar_altitude=direct_inclined_irradiance_series.refracted_solar_altitude,
        solar_azimuth=diffuse_inclined_irradiance_series.solar_azimuth,
        # azimuth_difference=azimuth_difference_series,
        #
        ## Positioning, Timing and Atmospheric algorithms
        solar_positioning_algorithm=direct_inclined_irradiance_series.solar_positioning_algorithm,
        solar_timing_algorithm=direct_inclined_irradiance_series.solar_timing_algorithm,
        adjusted_for_atmospheric_refraction=solar_altitude_series.adjusted_for_atmospheric_refraction,
        solar_incidence_model=direct_inclined_irradiance_series.solar_incidence_model,
        solar_incidence_definition=direct_inclined_irradiance_series.solar_incidence.definition,
        shading_algorithm=surface_in_shade_series.shading_algorithm,
        shading_states=shading_states,
        #
        ## Sources
        data_source=HOFIERKA_2002,
        solar_radiation_model=HOFIERKA_2002,
    )
