from zoneinfo import ZoneInfo
from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from pathlib import Path
from typing import Optional
import numpy as np
from rich import print
from pandas import DatetimeIndex
from pvgisprototype import SurfaceTilt
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype import SpectralFactorSeries
from pvgisprototype import PhotovoltaicPower
from pvgisprototype import PhotovoltaicPowerMultipleModules
from pvgisprototype.api.power.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.api.irradiance.models import MethodForInexactMatches
from pvgisprototype.api.position.models import SolarDeclinationModel
from pvgisprototype.api.position.models import SolarPositionModel
from pvgisprototype.api.position.models import SolarIncidenceModel
from pvgisprototype.api.position.models import SolarTimeModel
from pvgisprototype.api.position.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.position.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.power.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.validation.hashing import generate_hash
from pvgisprototype.constants import SOLAR_CONSTANT, ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT
from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import TIMESTAMPS_FREQUENCY_DEFAULT
from pvgisprototype.constants import UNITLESS
from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype.constants import SPECTRAL_FACTOR_COLUMN_NAME
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import LINKE_TURBIDITY_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import ALBEDO_DEFAULT
from pvgisprototype.constants import TIME_OFFSET_GLOBAL_DEFAULT
from pvgisprototype.constants import HOUR_OFFSET_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import LINKE_TURBIDITY_TIME_SERIES_DEFAULT
from pvgisprototype.constants import LINKE_TURBIDITY_UNIT
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import SYSTEM_EFFICIENCY_DEFAULT
from pvgisprototype.constants import EFFICIENCY_DEFAULT
from pvgisprototype.constants import POWER_UNIT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import IRRADIANCE_UNIT
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import TITLE_KEY_NAME
from pvgisprototype.constants import PHOTOVOLTAIC_POWER
from pvgisprototype.constants import PHOTOVOLTAIC_POWER_COLUMN_NAME
from pvgisprototype.constants import PHOTOVOLTAIC_MODULE_DEFAULT
from pvgisprototype.constants import EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EFFICIENCY_COLUMN_NAME
from pvgisprototype.constants import POWER_MODEL_COLUMN_NAME
from pvgisprototype.constants import GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import TEMPERATURE_COLUMN_NAME
from pvgisprototype.constants import WIND_SPEED_COLUMN_NAME
from pvgisprototype.constants import SURFACE_TILT_COLUMN_NAME
from pvgisprototype.constants import SURFACE_ORIENTATION_COLUMN_NAME
from pvgisprototype.constants import ABOVE_HORIZON_COLUMN_NAME
from pvgisprototype.constants import LOW_ANGLE_COLUMN_NAME
from pvgisprototype.constants import BELOW_HORIZON_COLUMN_NAME
from pvgisprototype.constants import SHADE_COLUMN_NAME
from pvgisprototype.constants import INCIDENCE_ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import ALTITUDE_COLUMN_NAME
from pvgisprototype.constants import AZIMUTH_COLUMN_NAME
from pvgisprototype.constants import SPECTRAL_FACTOR_DEFAULT
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype.constants import cPROFILE_FLAG_DEFAULT
from pvgisprototype.constants import MINUTES
from pvgisprototype.constants import LOG_LEVEL_DEFAULT
from pvgisprototype.constants import FINGERPRINT_FLAG_DEFAULT
from pvgisprototype.constants import ANGULAR_LOSS_FACTOR_FLAG_DEFAULT
from pvgisprototype.constants import NEIGHBOR_LOOKUP_DEFAULT
from pvgisprototype.constants import MULTI_THREAD_FLAG_DEFAULT
from pvgisprototype.api.power.broadband import calculate_photovoltaic_power_output_series
from pvgisprototype.validation.arrays import create_array
import cProfile, pstats, io


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
    timestamps: DatetimeIndex = None,
    timezone: Optional[ZoneInfo] = ZoneInfo('UTC'),
    global_horizontal_irradiance: Optional[Path] = None,
    direct_horizontal_irradiance: Optional[Path] = None,
    spectral_factor_series: SpectralFactorSeries = SpectralFactorSeries(value=SPECTRAL_FACTOR_DEFAULT),
    temperature_series: np.ndarray = np.array(TEMPERATURE_DEFAULT),
    wind_speed_series: np.ndarray = np.array(WIND_SPEED_DEFAULT),
    mask_and_scale: bool = MASK_AND_SCALE_FLAG_DEFAULT,
    neighbor_lookup: MethodForInexactMatches = NEIGHBOR_LOOKUP_DEFAULT,
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    in_memory: bool = IN_MEMORY_FLAG_DEFAULT,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = MULTI_THREAD_FLAG_DEFAULT,
    surface_orientation: list[float] = [SURFACE_ORIENTATION_DEFAULT],
    surface_tilt: list[float] = [SURFACE_TILT_DEFAULT],
    linke_turbidity_factor_series: LinkeTurbidityFactor = LINKE_TURBIDITY_TIME_SERIES_DEFAULT,
    apply_atmospheric_refraction: Optional[bool] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Optional[float] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Optional[float] = ALBEDO_DEFAULT,
    apply_angular_loss_factor: Optional[bool] = ANGULAR_LOSS_FACTOR_FLAG_DEFAULT,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.jenco,
    zero_negative_solar_incidence_angle: bool = ZERO_NEGATIVE_INCIDENCE_ANGLE_DEFAULT,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    angle_output_units: str = RADIANS,
    photovoltaic_module: PhotovoltaicModuleModel = PHOTOVOLTAIC_MODULE_DEFAULT, 
    system_efficiency: Optional[float] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: PhotovoltaicModulePerformanceModel = None,
    temperature_model: ModuleTemperatureAlgorithm = None,
    efficiency: Optional[float] = EFFICIENCY_DEFAULT,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = LOG_LEVEL_DEFAULT,
    fingerprint: bool = FINGERPRINT_FLAG_DEFAULT,
    profile: bool = cPROFILE_FLAG_DEFAULT,
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
    timestamps : Optional[DatetimeIndex], optional
        Specific timestamps for which to calculate the irradiance. Default is None.
    timezone : Optional[str], optional
         Timezone of the location, by default None
    global_horizontal_irradiance : Optional[Path], optional
        Path to global horizontal irradiance, by default None
    direct_horizontal_irradiance : Optional[Path], optional
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
    tolerance : Optional[float], optional
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
    refracted_solar_zenith : Optional[float], optional
        Apply atmospheric refraction option, by default REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
    albedo : Optional[float], optional
        Albedo, by default ALBEDO_DEFAULT
    apply_angular_loss_factor : Optional[bool], optional
        Apply angular loss fator, by default True
    solar_position_model : SolarPositionModel, optional
        Solar position model, by default SOLAR_POSITION_ALGORITHM_DEFAULT
    solar_incidence_model : SolarIncidenceModel, optional
        Solar incidence model, by default SolarIncidenceModel.jenco
    solar_time_model : SolarTimeModel, optional
        Solar time model, by default SOLAR_TIME_ALGORITHM_DEFAULT
    solar_constant : float, optional
        Solar constant, by default SOLAR_CONSTANT
    perigee_offset : float, optional
        Perigee offset value, by default PERIGEE_OFFSET
    eccentricity_correction_factor : float, optional
        Eccentricity correction factor, by default ECCENTRICITY_CORRECTION_FACTOR
    angle_output_units : str, optional
        Angle output units, by default RADIANS
    photovoltaic_module : PhotovoltaicModuleModel, optional
        Photovoltaic module, by default PHOTOVOLTAIC_MODULE_DEFAULT
    system_efficiency : Optional[float], optional
        System efficiency, by default SYSTEM_EFFICIENCY_DEFAULT
    power_model : PhotovoltaicModulePerformanceModel, optional
        Power model, by default None
    temperature_model : ModuleTemperatureAlgorithm, optional
        Temperature model, by default None
    efficiency : Optional[float], optional
        Module efficiency value, by default None
    verbose : int, optional
        Verbosing level, by default VERBOSE_LEVEL_DEFAULT
    log : int, optional
        Logging level, by default 0
    fingerprint : bool, optional
        Include output fingerprint, by default False
    profile : bool, optional
        Include profile, by default False

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
        "apply_atmospheric_refraction": apply_atmospheric_refraction,
        "refracted_solar_zenith": refracted_solar_zenith,
        "albedo": albedo,
        "apply_angular_loss_factor": apply_angular_loss_factor,
        "solar_position_model": solar_position_model,
        "solar_incidence_model": solar_incidence_model,
        "zero_negative_solar_incidence_angle": zero_negative_solar_incidence_angle,
        "solar_time_model": solar_time_model,
        "solar_constant": solar_constant,
        "perigee_offset": perigee_offset,
        "eccentricity_correction_factor": eccentricity_correction_factor,
        "angle_output_units": angle_output_units,
        "photovoltaic_module": photovoltaic_module,
        "system_efficiency": system_efficiency,
        "power_model": power_model,
        "temperature_model": temperature_model,
        "efficiency": efficiency,
        "verbose": 6,
        "log": log,
        "profile": profile,
        "fingerprint": fingerprint
        }

    if multi_thread:
        from multiprocessing.pool import ThreadPool as Pool
        from functools import partial
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
    photovoltaic_power_output_series = create_array(**array_parameters)
    global_irradiance_series = create_array(**array_parameters)
    direct_irradiance_series = create_array(**array_parameters)
    diffuse_irradiance_series = create_array(**array_parameters)
    reflected_irradiance_series = create_array(**array_parameters)
    effective_direct_irradiance_series = create_array(**array_parameters)
    effective_diffuse_irradiance_series = create_array(**array_parameters)
    effective_reflected_irradiance_series = create_array(**array_parameters)

    for photovoltaic_power_output in individual_photovoltaic_power_outputs:
        photovoltaic_power_output_series += photovoltaic_power_output.value
        global_irradiance_series += photovoltaic_power_output.components[
            GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME
        ]
        direct_irradiance_series += photovoltaic_power_output.components[
            DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
        ]
        diffuse_irradiance_series += photovoltaic_power_output.components[
            DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME
        ]
        reflected_irradiance_series += photovoltaic_power_output.components[
            REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME
        ]
        effective_direct_irradiance_series += photovoltaic_power_output.components[
            EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME
        ]
        effective_diffuse_irradiance_series += photovoltaic_power_output.components[
            EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME
        ]
        effective_reflected_irradiance_series += photovoltaic_power_output.components[
            EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME
        ]

    components_container = {
        'main': lambda: {
            TITLE_KEY_NAME: PHOTOVOLTAIC_POWER,
            PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series,
        },
        
        'extended': lambda: {
            TITLE_KEY_NAME: PHOTOVOLTAIC_POWER + " & in-plane components",
            POWER_MODEL_COLUMN_NAME: power_model.value if power_model else NOT_AVAILABLE,
            GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME: global_irradiance_series,
            DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME: direct_irradiance_series,
            DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME: diffuse_irradiance_series,
            REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME: reflected_irradiance_series,
        } if verbose > 1 else {},
        
        'more_extended': lambda: {
            EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME: effective_direct_irradiance_series,
            EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME: effective_diffuse_irradiance_series,
            EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME: effective_reflected_irradiance_series,
        } if verbose > 2 else {},
        
        'even_more_extended': lambda: {
            TEMPERATURE_COLUMN_NAME: temperature_series.value,
            WIND_SPEED_COLUMN_NAME: wind_speed_series.value,
            SPECTRAL_FACTOR_COLUMN_NAME: spectral_factor_series.value,
        } if verbose > 3 else {},

        'fingerprint': lambda: {
            FINGERPRINT_COLUMN_NAME: generate_hash(photovoltaic_power_output_series),
        } if fingerprint else {},
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
