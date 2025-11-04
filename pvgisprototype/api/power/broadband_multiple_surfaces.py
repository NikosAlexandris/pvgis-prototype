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
import cProfile
import io
import pstats
from pathlib import Path
from typing import List
from zoneinfo import ZoneInfo

import numpy as np
from devtools import debug
from pandas import DatetimeIndex, Timestamp
from rich import print
from xarray import DataArray

from pvgisprototype import (
    LinkeTurbidityFactor,
    PhotovoltaicPowerMultipleModules,
    SpectralFactorSeries,
    DirectHorizontalIrradiance,
    DiffuseSkyReflectedHorizontalIrradiance,
)
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.algorithms.huld.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    SUN_HORIZON_POSITION_DEFAULT,
    ShadingModel,
    ShadingState,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarSurfacePositionParameter,
    SolarTimeModel,
    SunHorizonPositionModel,
    select_models,
)
from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)
from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleModel, PhotovoltaicModuleType
from pvgisprototype.api.utilities.conversions import (
    convert_float_to_degrees_if_requested,
)
from pvgisprototype.constants import (
    ABOVE_HORIZON_COLUMN_NAME,
    ALBEDO_DEFAULT,
    ALTITUDE_COLUMN_NAME,
    ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    ARRAY_BACKEND_DEFAULT,
    ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    AZIMUTH_COLUMN_NAME,
    BELOW_HORIZON_COLUMN_NAME,
    DATA_TYPE_DEFAULT,
    DEBUG_AFTER_THIS_VERBOSITY_LEVEL,
    DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME,
    DIFFUSE_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME,
    DIRECT_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    ECCENTRICITY_CORRECTION_FACTOR,
    ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME,
    EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_GLOBAL_IRRADIANCE_COLUMN_NAME,
    EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME,
    EFFICIENCY_COLUMN_NAME,
    EFFICIENCY_FACTOR_DEFAULT,
    FINGERPRINT_COLUMN_NAME,
    FINGERPRINT_FLAG_DEFAULT,
    GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME,
    HASH_AFTER_THIS_VERBOSITY_LEVEL,
    IN_MEMORY_FLAG_DEFAULT,
    INCIDENCE_ALGORITHM_COLUMN_NAME,
    INCIDENCE_COLUMN_NAME,
    INCIDENCE_DEFINITION,
    LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    LOG_LEVEL_DEFAULT,
    LOW_ANGLE_COLUMN_NAME,
    MASK_AND_SCALE_FLAG_DEFAULT,
    MULTI_THREAD_FLAG_DEFAULT,
    NEIGHBOR_LOOKUP_DEFAULT,
    NOT_AVAILABLE,
    PEAK_POWER_COLUMN_NAME,
    ECCENTRICITY_PHASE_OFFSET,
    ECCENTRICITY_PHASE_OFFSET_COLUMN_NAME,
    PHOTOVOLTAIC_MODULE_DEFAULT,
    PHOTOVOLTAIC_POWER_NAME,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    POSITION_ALGORITHM_COLUMN_NAME,
    POWER_MODEL_COLUMN_NAME,
    POWER_UNIT,
    RADIANS,
    RADIATION_CUTOFF_THRESHHOLD,
    REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME,
    REFLECTED_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME,
    REFLECTIVITY_COLUMN_NAME,
    UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    SURFACE_IN_SHADE_COLUMN_NAME,
    SOLAR_CONSTANT,
    SOLAR_CONSTANT_COLUMN_NAME,
    SPECTRAL_EFFECT_COLUMN_NAME,
    SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME,
    SPECTRAL_FACTOR_COLUMN_NAME,
    SPECTRAL_FACTOR_DEFAULT,
    SURFACE_ORIENTATION_COLUMN_NAME,
    SURFACE_ORIENTATION_DEFAULT,
    SURFACE_TILT_COLUMN_NAME,
    SURFACE_TILT_DEFAULT,
    SYSTEM_EFFICIENCY_COLUMN_NAME,
    SYSTEM_EFFICIENCY_DEFAULT,
    TECHNOLOGY_NAME,
    TEMPERATURE_COLUMN_NAME,
    TEMPERATURE_DEFAULT,
    TIME_ALGORITHM_COLUMN_NAME,
    TITLE_KEY_NAME,
    TOLERANCE_DEFAULT,
    UNIT_NAME,
    VERBOSE_LEVEL_DEFAULT,
    WIND_SPEED_COLUMN_NAME,
    WIND_SPEED_DEFAULT,
    ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    cPROFILE_FLAG_DEFAULT,
    VALIDATE_OUTPUT_DEFAULT,
    VERBOSE_LEVEL_MULTI_MODULE_DEFAULT,
)
from pvgisprototype.log import log_data_fingerprint, log_function_call
from pvgisprototype.core.arrays import create_array
from pvgisprototype.core.hashing import generate_hash


def setup_profiler(enable_profiling):
    if enable_profiling:
        profiler = cProfile.Profile()
        profiler.enable()
        return profiler
    return None


def finalise_profiling(disable_profiling, profiler, verbose):
    if not disable_profiling or profiler is None:
        return
    profiler.disable()
    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()

    profile_filename = "profiling_stats.prof"
    profiler.dump_stats(profile_filename)
    print(f"Profiling statistics saved to {profile_filename}")

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        print(s.getvalue())


@log_function_call
def calculate_photovoltaic_power_output_series_from_multiple_surfaces(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz="UTC")]),
    timezone: ZoneInfo | None = ZoneInfo("UTC"),
    global_horizontal_irradiance: Path | None = None,
    direct_horizontal_irradiance: Path | None = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(
        value=SPECTRAL_FACTOR_DEFAULT
    ),
    temperature_series: np.ndarray = np.array(TEMPERATURE_DEFAULT),
    wind_speed_series: np.ndarray = np.array(WIND_SPEED_DEFAULT),
    surface_orientations: list[float] = [SURFACE_ORIENTATION_DEFAULT],
    surface_tilts: list[float] = [SURFACE_TILT_DEFAULT],
    linke_turbidity_factor_series: LinkeTurbidityFactor = LinkeTurbidityFactor(
        value=LINKE_TURBIDITY_TIME_SERIES_DEFAULT
    ),
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    # unrefracted_solar_zenith: UnrefractedSolarZenith | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: float | None = ALBEDO_DEFAULT,
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    sun_horizon_position: List[SunHorizonPositionModel] = SUN_HORIZON_POSITION_DEFAULT,
    #
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.jenco,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    #
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    shading_states: List[ShadingState] = [ShadingState.all],
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    #
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = ECCENTRICITY_PHASE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    #
    photovoltaic_module_type: PhotovoltaicModuleType = PhotovoltaicModuleType.Monofacial,  # Leave Me Like This !
    bifaciality_factor: float = 0.3, # 0.7,  # Fixed !
    photovoltaic_module: PhotovoltaicModuleModel = PHOTOVOLTAIC_MODULE_DEFAULT,
    peak_power: float = 1,
    #
    system_efficiency: float | None = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: PhotovoltaicModulePerformanceModel = None,
    radiation_cutoff_threshold: float = RADIATION_CUTOFF_THRESHHOLD,
    temperature_model: ModuleTemperatureAlgorithm = None,
    efficiency: float | None = EFFICIENCY_FACTOR_DEFAULT,
    #
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    #
    multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    angle_output_units: str = RADIANS,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
    profile: bool = cPROFILE_FLAG_DEFAULT,
    validate_output: bool = VALIDATE_OUTPUT_DEFAULT,
):
    """Estimate the total photovoltaic power for multiple solar surfaces.

    Estimate the total photovoltaic power for multiple solar surfaces, i.e.
    different pairs of surface orientation and tilt angles) over a time series
    or an arbitrarily aggregated energy production of a PV system based on the
    effective solar irradiance incident on a solar surface, the ambient
    temperature and optionally wind speed.

    Parameters
    ----------
    longitude : float
        The longitude of the location for which the energy production is calculated.
    latitude : float
        The latitude of the location.
    elevation : float
        Elevation of the location in meters.
    timestamps : DatetimeIndex, optional
        Specific timestamps for which to calculate the irradiance. Default is None.
    timezone : str, optional
         Timezone of the location, by default None
    global_horizontal_irradiance : Path | None, optional
        Path to global horizontal irradiance, by default None
    direct_horizontal_irradiance : Path | None, optional
        Path to direct horizontal irradiance, by default None
    spectral_factor_series : SpectralFactorSeries, optional
        Spectral factor values, by default SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT)
    temperature_series : np.ndarray, optional
        Series of temperature values, by default np.array(TEMPERATURE_DEFAULT)
    wind_speed_series : np.ndarray, optional
        Series of wind speed values, by default np.array(WIND_SPEED_DEFAULT)
    dtype : str, optional
        Datatype, by default DATA_TYPE_DEFAULT
    array_backend : str, optional
        Array backend option, by default ARRAY_BACKEND_DEFAULT
    multi_thread : bool, optional
        Calculations with multithread, by default True
    surface_orientations : list[float], optional
        List of orientation values, by default [SURFACE_ORIENTATION_DEFAULT]
    surface_tilts : list[float], optional
        List of tilt values, by default [SURFACE_TILT_DEFAULT]
    linke_turbidity_factor_series : LinkeTurbidityFactor, optional
        Linke turbidity factor values, by default [LINKE_TURBIDITY_TIME_SERIES_DEFAULT]
    refracted_solar_zenith : float | None, optional
        Apply atmospheric refraction option, by default UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
    albedo : float | None, optional
        Albedo, by default ALBEDO_DEFAULT
    apply_reflectivity_factor : bool, optional
        Apply angular loss fator, by default True
    solar_position_model : SolarPositionModel, optional
        Solar position model, by default SOLAR_POSITION_ALGORITHM_DEFAULT
    solar_incidence_model : SolarIncidenceModel, optional
        Solar incidence model, by default SolarIncidenceModel.jenco
    solar_time_model : SolarTimeModel, optional
        Solar time model, by default SOLAR_TIME_ALGORITHM_DEFAULT
    solar_constant : float, optional
        Solar constant, by default SOLAR_CONSTANT
    eccentricity_phase_offset : float, optional
        Perigee offset value, by default ECCENTRICITY_PHASE_OFFSET
    eccentricity_amplitude : float, optional
        Eccentricity correction factor, by default ECCENTRICITY_CORRECTION_FACTOR
    angle_output_units : str, optional
        Angle output units, by default RADIANS
    photovoltaic_module : PhotovoltaicModuleModel, optional
        Photovoltaic module, by default PHOTOVOLTAIC_MODULE_DEFAULT
    system_efficiency : float | None, optional
        System efficiency, by default SYSTEM_EFFICIENCY_DEFAULT
    power_model : PhotovoltaicModulePerformanceModel, optional
        Power model, by default None
    temperature_model : ModuleTemperatureAlgorithm, optional
        Temperature model, by default None
    efficiency : float | None, optional
        Module efficiency value, by default None
    verbose : int, optional
        Verbosing level, by default VERBOSE_LEVEL_DEFAULT
    log : int, optional
        Logging level, by default 0
    fingerprint : bool, optional
        Include output fingerprint, by default False
    profile : bool, optional
        Include profile, by default False
    validate_output: bool, optional
        Perform validation on the output of each function
    Returns
    -------
    PhotovoltaicPowerMultipleModules
        Summary of array of effective irradiance values.

    """
    profiler = setup_profiler(enable_profiling=profile)

    pairs_of_surface_orientation_and_tilt_angles = (
        {SolarSurfacePositionParameter.surface_orientation.name: orientation,
         SolarSurfacePositionParameter.surface_tilt.name: tilt}
        for orientation, tilt in zip(surface_orientations, surface_tilts)
    )
    sun_horizon_positions = select_models(SunHorizonPositionModel, sun_horizon_position)
    common_parameters = {
        "longitude": longitude,
        "latitude": latitude,
        "elevation": elevation,
        #
        "timestamps": timestamps,
        "timezone": timezone,
        #
        "global_horizontal_irradiance": global_horizontal_irradiance,
        "direct_horizontal_irradiance": direct_horizontal_irradiance,
        "spectral_factor_series": spectral_factor_series,
        "temperature_series": temperature_series,
        "wind_speed_series": wind_speed_series,
        #
        "linke_turbidity_factor_series": linke_turbidity_factor_series,
        "adjust_for_atmospheric_refraction": adjust_for_atmospheric_refraction,
        # "unrefracted_solar_zenith": unrefracted_solar_zenith,
        "albedo": albedo,
        #
        "apply_reflectivity_factor": apply_reflectivity_factor,
        "solar_position_model": solar_position_model,
        "sun_horizon_position": sun_horizon_position,
        #
        "solar_incidence_model": solar_incidence_model,
        "zero_negative_solar_incidence_angle": zero_negative_solar_incidence_angle,
        #
        "horizon_profile": horizon_profile,
        "shading_model": shading_model,
        "shading_states": shading_states,
        "solar_time_model": solar_time_model,
        #
        "solar_constant": solar_constant,
        "eccentricity_phase_offset": eccentricity_phase_offset,
        "eccentricity_amplitude": eccentricity_amplitude,
        #
        "photovoltaic_module_type": photovoltaic_module_type,
        "bifaciality_factor": bifaciality_factor,
        "photovoltaic_module": photovoltaic_module,
        "peak_power": peak_power,
        #
        "system_efficiency": system_efficiency,
        "power_model": power_model,
        "radiation_cutoff_threshold": radiation_cutoff_threshold,
        "temperature_model": temperature_model,
        "efficiency": efficiency,
        #
        "dtype": dtype,
        "array_backend": array_backend,
        #
        # "angle_output_units": angle_output_units,
        "validate_output": validate_output,
        "verbose": VERBOSE_LEVEL_MULTI_MODULE_DEFAULT,
        "log": log,
        "fingerprint": fingerprint,
        "profile": profile,
    }
    if multi_thread:
        from functools import partial
        from multiprocessing.pool import ThreadPool as Pool

        pool = Pool()
        partial_calculate_photovoltaic_power_output_series = partial(
            calculate_photovoltaic_power_output_series, **common_parameters
        )
        individual_photovoltaic_power_outputs = pool.map(
            lambda args: partial_calculate_photovoltaic_power_output_series(**args),
            pairs_of_surface_orientation_and_tilt_angles,
        )
        pool.close()

    else:
        individual_photovoltaic_power_outputs = [
            calculate_photovoltaic_power_output_series(
                **common_parameters,
                **surface_position_angles,
            )
            for surface_position_angles in pairs_of_surface_orientation_and_tilt_angles
        ]

    array_parameters = {
        "shape": timestamps.shape,
        "dtype": dtype,
        "init_method": "zeros",
        "backend": array_backend,
    }  # Borrow shape from timestamps

    # Irradiance after reflectivity ?
    total_global_inclined_irradiance = create_array(**array_parameters)
    total_direct_inclined_irradiance = create_array(**array_parameters)
    total_diffuse_inclined_irradiance = create_array(**array_parameters)

    # In-plane (or inclined) irradiance **before reflectivity**
    total_direct_inclined_irradiance_before_reflectivity = create_array(
        **array_parameters
    )
    total_diffuse_inclined_irradiance_before_reflectivity = create_array(
        **array_parameters
    )
    total_ground_reflected_inclined_irradiance_before_reflectivity = create_array(
        **array_parameters
    )
    # sum of the above three =
    total_global_inclined_irradiance_before_reflectivity = create_array(
        **array_parameters
    )

    # reflectivity effect factor as a function of the incidence angle
    total_direct_inclined_reflectivity_factor = create_array(**array_parameters)
    total_diffuse_inclined_reflectivity_factor = create_array(**array_parameters)
    total_ground_reflected_inclined_reflectivity_factor = create_array(
        **array_parameters
    )
    # ... --- Does this make sense at this point ?
    total_global_inclined_reflected = create_array(**array_parameters)

    # after the reflectivity effect
    total_ground_reflected_inclined_irradiance = create_array(**array_parameters)
    total_direct_horizontal_irradiance = DirectHorizontalIrradiance(
        value= create_array(**array_parameters),
        # out_of_range=out_of_range,
        # out_of_range_index=out_of_range_index,
        elevation=elevation,
        # solar_altitude=solar_altitude_series,
        # refracted_solar_altitude=refracted_solar_altitude_series.value,
        # optical_air_mass=optical_air_mass_series,
        # direct_normal_irradiance=direct_normal_irradiance_series,
        # surface_in_shade=surface_in_shade_series,
        # solar_radiation_model=HOFIERKA_2002,
        # data_source=HOFIERKA_2002,
    )
    total_diffuse_horizontal_irradiance = DiffuseSkyReflectedHorizontalIrradiance(
        value= create_array(**array_parameters),
        # out_of_range=out_of_range,
        # out_of_range_index=out_of_range_index,
        # extraterrestrial_normal_irradiance=extraterrestrial_normal_irradiance_series,
        linke_turbidity_factor=linke_turbidity_factor_series,
        # solar_altitude=solar_altitude_series,
        # solar_positioning_algorithm=solar_altitude_series.solar_positioning_algorithm,
        # adjust_for_atmospheric_refraction=solar_altitude_series.adjusted_for_atmospheric_refraction,
    )
    global_irradiance_series = create_array(**array_parameters)

    #
    photovoltaic_power_output_without_system_loss_series = create_array(
        **array_parameters
    )
    photovoltaic_power_output_series = create_array(**array_parameters)

    # same for all years, applies to global or any component
    total_spectral_effect = create_array(**array_parameters)
    total_effective_direct_irradiance = create_array(**array_parameters)
    total_effective_diffuse_irradiance = create_array(**array_parameters)
    total_effective_reflected_inclined_irradiance = create_array(**array_parameters)
    # sum of above three
    total_effective_global_irradiance = create_array(**array_parameters)

    # sun_horizon_positions = []

    for photovoltaic_power_output in individual_photovoltaic_power_outputs:
        photovoltaic_power_output_series += photovoltaic_power_output.value
        global_irradiance_series += photovoltaic_power_output.global_inclined_irradiance
        photovoltaic_power_output_without_system_loss_series += (
            photovoltaic_power_output.photovoltaic_power_without_system_loss
        )
        total_effective_global_irradiance += (
            photovoltaic_power_output.effective_global_irradiance
        )
        total_effective_direct_irradiance += (
            photovoltaic_power_output.effective_direct_irradiance
        )
        total_effective_diffuse_irradiance += (
            photovoltaic_power_output.effective_diffuse_irradiance
        )
        total_effective_reflected_inclined_irradiance += (
            photovoltaic_power_output.effective_ground_reflected_irradiance
        )
        total_spectral_effect += photovoltaic_power_output.spectral_effect

        if apply_reflectivity_factor:
            # the amount after the reflectivity effect !
            total_global_inclined_reflected += (
                photovoltaic_power_output.global_inclined_reflected
            )
            total_direct_inclined_reflectivity_factor += (
                photovoltaic_power_output.direct_inclined_reflectivity_factor
            )
            total_diffuse_inclined_reflectivity_factor += (
                photovoltaic_power_output.diffuse_inclined_reflectivity_factor
            )
            total_ground_reflected_inclined_reflectivity_factor += (
                photovoltaic_power_output.ground_reflected_inclined_reflectivity_factor
            )

        total_global_inclined_irradiance += (
            photovoltaic_power_output.global_inclined_irradiance
        )
        total_direct_inclined_irradiance += (
            photovoltaic_power_output.direct_inclined_irradiance
        )
        total_diffuse_inclined_irradiance += (
            photovoltaic_power_output.diffuse_inclined_irradiance
        )
        total_ground_reflected_inclined_irradiance += (
            photovoltaic_power_output.ground_reflected_inclined_irradiance
        )

        # Irradiance before reflectivity effect

        total_global_inclined_irradiance_before_reflectivity += (
            photovoltaic_power_output.ground_reflected_inclined_before_reflectivity
            if apply_reflectivity_factor
            else photovoltaic_power_output.global_inclined_irradiance
        )
        total_direct_inclined_irradiance_before_reflectivity += (
            photovoltaic_power_output.direct_inclined_before_reflectivity
            if apply_reflectivity_factor
            else photovoltaic_power_output.direct_inclined_irradiance
        )
        total_diffuse_inclined_irradiance_before_reflectivity += (
            photovoltaic_power_output.diffuse_inclined_before_reflectivity
            if apply_reflectivity_factor
            else photovoltaic_power_output.diffuse_inclined_irradiance
        )
        total_ground_reflected_inclined_irradiance_before_reflectivity += (
            photovoltaic_power_output.ground_reflected_inclined_before_reflectivity
            if apply_reflectivity_factor
            else photovoltaic_power_output.ground_reflected_inclined_irradiance
        )
        total_direct_horizontal_irradiance.value += (
            photovoltaic_power_output.direct_horizontal_irradiance.value
        )
        total_diffuse_horizontal_irradiance.value += (
            photovoltaic_power_output.diffuse_horizontal_irradiance.value
        )

        # # Plus, some metadata
        # sun_horizon_positions.append(photovoltaic_power_output.sun_horizon_positions)

    total_spectral_effect_percentage = (
        (total_spectral_effect / global_irradiance_series * 100)
        if global_irradiance_series is not None
        else 0
    )

    if verbose > DEBUG_AFTER_THIS_VERBOSITY_LEVEL:
        debug(locals())

    if profile:
        finalise_profiling(
            disable_profiling=~profile,  # Inverted confusing logic !
            profiler=profiler,
            verbose=verbose,
        )

    log_data_fingerprint(
        data=photovoltaic_power_output_series,
        log_level=log,
        hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )

    photovoltaic_power = PhotovoltaicPowerMultipleModules(
        value=photovoltaic_power_output_series,
        modules=individual_photovoltaic_power_outputs,
        individual_series=individual_photovoltaic_power_outputs,
        # out_of_range=out_of_range,
        # out_of_range_index=out_of_range_index,
        # unit=POWER_UNIT,
        technology=photovoltaic_module.value,
        power_model=power_model.value,
        system_efficiency=system_efficiency,
        efficiency_factor=individual_photovoltaic_power_outputs[0].efficiency_factor,
        temperature=temperature_series,
        wind_speed=wind_speed_series,
        #
        ## Effective Irradiance Components
        effective_global_irradiance=total_effective_global_irradiance,
        effective_direct_irradiance=total_effective_direct_irradiance,
        effective_diffuse_irradiance=total_effective_diffuse_irradiance,
        effective_ground_reflected_irradiance=total_effective_reflected_inclined_irradiance,
        spectral_effect=total_spectral_effect,
        spectral_effect_percentage=total_spectral_effect_percentage,
        spectral_factor=spectral_factor_series,
        peak_power=peak_power,
        #
        ## Inclined Irradiance Components
        global_inclined_irradiance=total_global_inclined_irradiance,
        direct_inclined_irradiance=total_direct_inclined_irradiance,
        diffuse_inclined_irradiance=total_diffuse_inclined_irradiance,
        ground_reflected_inclined_irradiance=total_ground_reflected_inclined_irradiance,
        #
        ## Horizontal Irradiance Components
        irradiance=global_irradiance_series,
        global_horizontal_irradiance=global_horizontal_irradiance,
        direct_horizontal_irradiance=total_direct_horizontal_irradiance,
        diffuse_horizontal_irradiance=total_diffuse_horizontal_irradiance,
        #
        ## Components of the Extraterrestrial irradiance
        extraterrestrial_horizontal_irradiance=individual_photovoltaic_power_outputs[0].extraterrestrial_horizontal_irradiance,
        extraterrestrial_normal_irradiance=individual_photovoltaic_power_outputs[0].extraterrestrial_normal_irradiance,
        # linke_turbidity_factor=linke_turbidity_factor_series,
        #
        ## Location and Position
        # location=,
        elevation=elevation,
        surface_orientations=surface_orientations,
        surface_tilts=surface_tilts,
        surface_position_angle_pairs=list(zip(surface_orientations, surface_tilts)),
        sun_horizon_positions=sun_horizon_positions,
        #
        ## Solar Position parameters
        horizon_height=individual_photovoltaic_power_outputs[0].surface_in_shade.horizon_height,
        surface_in_shade=individual_photovoltaic_power_outputs[0].surface_in_shade,
        visible=individual_photovoltaic_power_outputs[0].surface_in_shade.visible,
        solar_incidence=individual_photovoltaic_power_outputs[0].solar_incidence, # This is not correct !
        shading_state=individual_photovoltaic_power_outputs[0].shading_state,
        sun_horizon_position=individual_photovoltaic_power_outputs[0].sun_horizon_position,  # positions != sun_horizon_positions
        solar_altitude=individual_photovoltaic_power_outputs[0].solar_altitude,
        # refracted_solar_altitude=individual_photovoltaic_power_outputs[0].refracted_solar_altitude,
        solar_azimuth=individual_photovoltaic_power_outputs[0].solar_azimuth,
        solar_azimuth_origin=individual_photovoltaic_power_outputs[0].solar_azimuth.origin,
        # azimuth_difference=azimuth_difference_series,
        #
        ## Positioning, Timing and Atmospheric algorithms
        angle_output_units=individual_photovoltaic_power_outputs[0].solar_incidence.unit, # Maybe get from surface_[prientation|tilt] ?
        # solar_positioning_algorithm=individual_photovoltaic_power_outputs[0].solar_positioning_algorithm,
        solar_positioning_algorithm="",
        # solar_timing_algorithm=individual_photovoltaic_power_outputs[0].solar_timing_algorithm,
        solar_timing_algorithm="",
        adjusted_for_atmospheric_refraction=individual_photovoltaic_power_outputs[0].adjusted_for_atmospheric_refraction,
        solar_incidence_model=individual_photovoltaic_power_outputs[0].solar_incidence_model,
        solar_incidence_definition=individual_photovoltaic_power_outputs[0].solar_incidence.definition,
        #     SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
        #     ECCENTRICITY_PHASE_OFFSET_COLUMN_NAME: eccentricity_phase_offset,
        #     ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_amplitude,
        shading_algorithm=individual_photovoltaic_power_outputs[0].shading_algorithm,
        shading_states=shading_states,
    )

    photovoltaic_power.build_output(
        verbose=verbose, fingerprint=fingerprint
    )

    return photovoltaic_power
