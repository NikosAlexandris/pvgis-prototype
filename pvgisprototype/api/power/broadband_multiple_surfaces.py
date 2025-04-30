import cProfile
import io
import pstats
from pathlib import Path
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
)
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import (
    SOLAR_POSITION_ALGORITHM_DEFAULT,
    SOLAR_TIME_ALGORITHM_DEFAULT,
    ShadingModel,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.power.broadband import (
    calculate_photovoltaic_power_output_series,
)
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
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
    PERIGEE_OFFSET,
    PERIGEE_OFFSET_COLUMN_NAME,
    PHOTOVOLTAIC_MODULE_DEFAULT,
    PHOTOVOLTAIC_POWER_NAME,
    PHOTOVOLTAIC_POWER_COLUMN_NAME,
    PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME,
    POSITION_ALGORITHM_COLUMN_NAME,
    POWER_MODEL_COLUMN_NAME,
    POWER_UNIT,
    RADIANS,
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
    timestamps: DatetimeIndex | None = DatetimeIndex([Timestamp.now(tz='UTC')]),
    timezone: ZoneInfo | None = ZoneInfo("UTC"),
    global_horizontal_irradiance: Path | None = None,
    direct_horizontal_irradiance: Path | None = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(
        value=SPECTRAL_FACTOR_DEFAULT
    ),
    temperature_series: np.ndarray = np.array(TEMPERATURE_DEFAULT),
    wind_speed_series: np.ndarray = np.array(WIND_SPEED_DEFAULT),
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    neighbor_lookup: MethodForInexactMatches = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: float | None = TOLERANCE_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    surface_orientation: list[float] = [SURFACE_ORIENTATION_DEFAULT],
    surface_tilt: list[float] = [SURFACE_TILT_DEFAULT],
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    adjust_for_atmospheric_refraction: bool = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    # unrefracted_solar_zenith: UnrefractedSolarZenith | None = UNREFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: float | None = ALBEDO_DEFAULT,
    apply_reflectivity_factor: bool = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.jenco,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    horizon_profile: DataArray | None = None,
    shading_model: ShadingModel = ShadingModel.pvis,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    eccentricity_phase_offset: float = PERIGEE_OFFSET,
    eccentricity_amplitude: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    photovoltaic_module: PhotovoltaicModuleModel = PHOTOVOLTAIC_MODULE_DEFAULT,
    peak_power: float = 1,
    system_efficiency: float | None = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: PhotovoltaicModulePerformanceModel = None,
    temperature_model: ModuleTemperatureAlgorithm = None,
    efficiency: float | None = EFFICIENCY_FACTOR_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
    profile: bool = cPROFILE_FLAG_DEFAULT,
    validate_output:bool = VALIDATE_OUTPUT_DEFAULT,
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
    mask_and_scale : bool, optional
         If True, applies masking and scaling to the input data, by default False
    neighbor_lookup : MethodForInexactMatches, optional
        Coordinates proximity setting, by default None
    tolerance : float | None, optional
        Tolerance, by default TOLERANCE_DEFAULT
    in_memory : bool, optional
        In memory option, by default False
    dtype : str, optional
        Datatype, by default DATA_TYPE_DEFAULT
    array_backend : str, optional
        Array backend option, by default ARRAY_BACKEND_DEFAULT
    multi_thread : bool, optional
        Calculations with multithread, by default True
    surface_orientation : list[float], optional
        List of orientation values, by default [SURFACE_ORIENTATION_DEFAULT]
    surface_tilt : list[float], optional
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
        Perigee offset value, by default PERIGEE_OFFSET
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
        {"surface_orientation": orientation, "surface_tilt": tilt}
        for orientation, tilt in zip(surface_orientation, surface_tilt)
    )
    common_parameters = {
        "longitude": longitude,
        "latitude": latitude,
        "elevation": elevation,
        "timestamps": timestamps,
        "timezone": timezone,
        "global_horizontal_irradiance": global_horizontal_irradiance,
        "direct_horizontal_irradiance": direct_horizontal_irradiance,
        "spectral_factor_series": spectral_factor_series,
        "temperature_series": temperature_series,
        "wind_speed_series": wind_speed_series,
        "neighbor_lookup": neighbor_lookup,
        "tolerance": tolerance,
        "mask_and_scale": mask_and_scale,
        "in_memory": in_memory,
        "dtype": dtype,
        "array_backend": array_backend,
        "linke_turbidity_factor_series": linke_turbidity_factor_series,
        "adjust_for_atmospheric_refraction": adjust_for_atmospheric_refraction,
        "refracted_solar_zenith": refracted_solar_zenith,
        "albedo": albedo,
        "apply_reflectivity_factor": apply_reflectivity_factor,
        "solar_position_model": solar_position_model,
        "solar_incidence_model": solar_incidence_model,
        "zero_negative_solar_incidence_angle": zero_negative_solar_incidence_angle,
        "horizon_profile": horizon_profile,
        "shading_model": shading_model,
        "solar_time_model": solar_time_model,
        "solar_constant": solar_constant,
        "eccentricity_phase_offset": eccentricity_phase_offset,
        "eccentricity_amplitude": eccentricity_amplitude,
        "angle_output_units": angle_output_units,
        "photovoltaic_module": photovoltaic_module,
        "system_efficiency": system_efficiency,
        "power_model": power_model,
        "temperature_model": temperature_model,
        "efficiency": efficiency,
        "verbose": VERBOSE_LEVEL_MULTI_MODULE_DEFAULT,
        "log": log,
        "profile": profile,
        "fingerprint": fingerprint,
        "peak_power": peak_power,
        "validate_output": validate_output,
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
    total_global_inclined_reflectivity = create_array(**array_parameters)

    # after the reflectivity effect
    total_ground_reflected_inclined_irradiance = create_array(**array_parameters)
    total_direct_horizontal_irradiance = create_array(**array_parameters)
    total_diffuse_horizontal_irradiance = create_array(**array_parameters)
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

    for photovoltaic_power_output in individual_photovoltaic_power_outputs:
        photovoltaic_power_output_series += photovoltaic_power_output.value
        global_irradiance_series += photovoltaic_power_output.components[
            GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME
        ]
        photovoltaic_power_output_without_system_loss_series += (
            photovoltaic_power_output.components[
                PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME
            ]
        )
        total_effective_global_irradiance += (
            photovoltaic_power_output.components[GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME]
            * photovoltaic_power_output.components[EFFICIENCY_COLUMN_NAME]
        )
        total_effective_direct_irradiance += (
            photovoltaic_power_output.components[DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME]
            * photovoltaic_power_output.components[EFFICIENCY_COLUMN_NAME]
        )
        total_effective_diffuse_irradiance += (
            photovoltaic_power_output.components[
                DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME
            ]
            * photovoltaic_power_output.components[EFFICIENCY_COLUMN_NAME]
        )
        total_effective_reflected_inclined_irradiance += (
            photovoltaic_power_output.components[
                REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME
            ]
            * photovoltaic_power_output.components[EFFICIENCY_COLUMN_NAME]
        )
        total_spectral_effect += photovoltaic_power_output.components[
            SPECTRAL_EFFECT_COLUMN_NAME
        ]

        if apply_reflectivity_factor:
            # the amount after the reflectivity effect !
            total_global_inclined_reflectivity += photovoltaic_power_output.components[
                REFLECTIVITY_COLUMN_NAME
            ]
            total_direct_inclined_reflectivity_factor += (
                photovoltaic_power_output.components[
                    DIRECT_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME
                ]
            )
            total_diffuse_inclined_reflectivity_factor += (
                photovoltaic_power_output.components[
                    DIFFUSE_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME
                ]
            )
            total_ground_reflected_inclined_reflectivity_factor += (
                photovoltaic_power_output.components[
                    REFLECTED_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME
                ]
            )

        total_global_inclined_irradiance += photovoltaic_power_output.components[
            GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME
        ]
        total_direct_inclined_irradiance += photovoltaic_power_output.components[
            DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
        ]
        total_diffuse_inclined_irradiance += photovoltaic_power_output.components[
            DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME
        ]
        total_ground_reflected_inclined_irradiance += (
            photovoltaic_power_output.components[
                REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME
            ]
        )

        # Irradiance before reflectivity effect
        total_global_inclined_irradiance_before_reflectivity += photovoltaic_power_output.components[
            GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME
        ] if apply_reflectivity_factor else photovoltaic_power_output.components[
            GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME]

        total_direct_inclined_irradiance_before_reflectivity += photovoltaic_power_output.components[
            DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME
        ] if apply_reflectivity_factor else photovoltaic_power_output.components[
            DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME]

        total_diffuse_inclined_irradiance_before_reflectivity += photovoltaic_power_output.components[
            DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME
        ] if apply_reflectivity_factor else photovoltaic_power_output.components[
            DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME]

        total_ground_reflected_inclined_irradiance_before_reflectivity += photovoltaic_power_output.components[
            REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME
        ] if apply_reflectivity_factor else photovoltaic_power_output.components[
            REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME]

        total_direct_horizontal_irradiance += photovoltaic_power_output.components[
            DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
        ]
        total_diffuse_horizontal_irradiance += photovoltaic_power_output.components[
            DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME
        ]

    total_spectral_effect_percentage = (
        (total_spectral_effect / global_irradiance_series * 100)
        if global_irradiance_series is not None
        else 0
    )

    components_container = {
        "Metadata": lambda: {
            POSITION_ALGORITHM_COLUMN_NAME: individual_photovoltaic_power_outputs[
                0
            ].components[POSITION_ALGORITHM_COLUMN_NAME],
            TIME_ALGORITHM_COLUMN_NAME: individual_photovoltaic_power_outputs[
                0
            ].components[TIME_ALGORITHM_COLUMN_NAME],
            SOLAR_CONSTANT_COLUMN_NAME: solar_constant,
            PERIGEE_OFFSET_COLUMN_NAME: eccentricity_phase_offset,
            ECCENTRICITY_CORRECTION_FACTOR_COLUMN_NAME: eccentricity_amplitude,
        },
        "Power": lambda: {
            TITLE_KEY_NAME: PHOTOVOLTAIC_POWER_NAME,
            PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series,
            TECHNOLOGY_NAME: photovoltaic_module.value,
            PEAK_POWER_COLUMN_NAME: peak_power,
            POWER_MODEL_COLUMN_NAME: (
                power_model.value if power_model else NOT_AVAILABLE
            ),
        },
        "Power extended": lambda: (
            {
                PHOTOVOLTAIC_POWER_WITHOUT_SYSTEM_LOSS_COLUMN_NAME: photovoltaic_power_output_without_system_loss_series,
            }
            if verbose > 1
            else {}
        ),
        "System loss": lambda: (
            {
                EFFICIENCY_COLUMN_NAME: individual_photovoltaic_power_outputs[
                    0
                ].components[EFFICIENCY_COLUMN_NAME],
                SYSTEM_EFFICIENCY_COLUMN_NAME: system_efficiency,
            }
            if verbose > 2
            else {}
        ),
        "Effective irradiance": lambda: (
            {
                TITLE_KEY_NAME: PHOTOVOLTAIC_POWER_COLUMN_NAME + " & effective components",
                EFFECTIVE_GLOBAL_IRRADIANCE_COLUMN_NAME: total_effective_global_irradiance,
                EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME: total_effective_direct_irradiance,
                EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME: total_effective_diffuse_irradiance,
                EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME: total_effective_reflected_inclined_irradiance,
                SPECTRAL_EFFECT_COLUMN_NAME: total_spectral_effect,
                SPECTRAL_EFFECT_PERCENTAGE_COLUMN_NAME: total_spectral_effect_percentage,
                SPECTRAL_FACTOR_COLUMN_NAME: individual_photovoltaic_power_outputs[
                    0
                ].components[SPECTRAL_FACTOR_COLUMN_NAME],
            }
            if verbose > 3
            else {}
        ),
        "Reflectivity": lambda: (
            {
                REFLECTIVITY_COLUMN_NAME: total_global_inclined_reflectivity,
                DIRECT_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME: total_direct_inclined_reflectivity_factor,
                DIFFUSE_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME: total_diffuse_inclined_reflectivity_factor,
                REFLECTED_INCLINED_IRRADIANCE_REFLECTIVITY_COLUMN_NAME: total_ground_reflected_inclined_reflectivity_factor,
            }
            if verbose > 6 and apply_reflectivity_factor
            else {}
        ),
        "Inclined irradiance components": lambda: (
            {
                GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME: total_global_inclined_irradiance,
                DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME: total_direct_inclined_irradiance,
                DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME: total_diffuse_inclined_irradiance,
                REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME: total_ground_reflected_inclined_irradiance,
            }
            if verbose > 4
            else {}
        ),
        "more_extended_2": lambda: (
            {
                TITLE_KEY_NAME: PHOTOVOLTAIC_POWER_COLUMN_NAME
                + ", effective & in-plane components",
                GLOBAL_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: total_global_inclined_irradiance_before_reflectivity,
                DIRECT_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: total_direct_inclined_irradiance_before_reflectivity,
                DIFFUSE_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: total_diffuse_inclined_irradiance_before_reflectivity,
                REFLECTED_INCLINED_IRRADIANCE_BEFORE_REFLECTIVITY_COLUMN_NAME: total_ground_reflected_inclined_irradiance_before_reflectivity,
            }
            if verbose > 5 and apply_reflectivity_factor
            else {}
        ),
        "Horizontal irradiance components": lambda: (
            {
                DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME: total_direct_horizontal_irradiance,
                DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: total_diffuse_horizontal_irradiance,
            }
            if verbose > 6
            else {}
        ),
        "Meteorological variables": lambda: (
            {
                TEMPERATURE_COLUMN_NAME: individual_photovoltaic_power_outputs[
                    0
                ].components[TEMPERATURE_COLUMN_NAME],
                WIND_SPEED_COLUMN_NAME: individual_photovoltaic_power_outputs[
                    0
                ].components[WIND_SPEED_COLUMN_NAME],
            }
            if verbose > 7
            else {}
        ),
        "Surface position": lambda: (
            {
                SURFACE_ORIENTATION_COLUMN_NAME: [
                    convert_float_to_degrees_if_requested(
                        surface_orientation_value, angle_output_units
                    )
                    for surface_orientation_value in surface_orientation
                ],
                SURFACE_TILT_COLUMN_NAME: [
                    convert_float_to_degrees_if_requested(
                        surface_tilt_value, angle_output_units
                    )
                    for surface_tilt_value in surface_tilt
                ],
            }
            if verbose > 8
            else {}
        ),
        "Indvidual series": lambda: (
            {
                f"Surface #{idx}": indvidual_photovoltaic_power_output.components for idx, indvidual_photovoltaic_power_output in enumerate(individual_photovoltaic_power_outputs)
            }
            if verbose > 9
            else {}
        ),
        "fingerprint": lambda: (
            {
                FINGERPRINT_COLUMN_NAME: generate_hash(
                    photovoltaic_power_output_series
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

    return PhotovoltaicPowerMultipleModules(
        series=photovoltaic_power_output_series,
        unit=POWER_UNIT,
        position_algorithm="",
        timing_algorithm="",
        elevation=elevation,
        surface_position_angle_pairs=list(zip(surface_orientation, surface_tilt)),
        irradiance=global_irradiance_series,
        modules=individual_photovoltaic_power_outputs,
        components=components,
        individual_series=individual_photovoltaic_power_outputs,
    )
