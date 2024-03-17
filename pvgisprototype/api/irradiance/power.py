from pvgisprototype.log import logger
from pvgisprototype.log import log_function_call
from pvgisprototype.log import log_data_fingerprint
from devtools import debug
from pathlib import Path
from math import cos
from typing import Annotated
from typing import List
from typing import Optional
import math
import numpy as np
from enum import Enum
from rich import print
from datetime import datetime
from pvgisprototype.api.geometry.models import SolarDeclinationModel
from pvgisprototype.api.geometry.models import SolarPositionModel
from pvgisprototype.api.geometry.models import SolarIncidenceModel
from pvgisprototype.api.geometry.models import SolarTimeModel
from pvgisprototype.api.geometry.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours_time_series
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithm
from pvgisprototype.api.irradiance.models import ModuleTemperatureAlgorithm
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.cli.print import print_irradiance_table_2
from pvgisprototype.api.irradiance.shade import is_surface_in_shade_time_series
from pvgisprototype.api.irradiance.direct import calculate_direct_inclined_irradiance_time_series_pvgis
from pvgisprototype.api.irradiance.diffuse import calculate_diffuse_inclined_irradiance_time_series
from pvgisprototype.api.irradiance.reflected import calculate_ground_reflected_inclined_irradiance_time_series
from pvgisprototype.api.geometry.altitude_series import model_solar_altitude_time_series
from pvgisprototype.api.geometry.azimuth_series import model_solar_azimuth_time_series
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.constants import FINGERPRINT_COLUMN_NAME
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.constants import ARRAY_BACKEND_DEFAULT
from pvgisprototype.constants import TIMESTAMPS_FREQUENCY_DEFAULT
from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype.constants import TEMPERATURE_UNIT
from pvgisprototype.constants import WIND_SPEED_DEFAULT
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
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import SYSTEM_EFFICIENCY_DEFAULT
from pvgisprototype.constants import EFFICIENCY_DEFAULT
from pvgisprototype.constants import POWER_UNIT
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import HASH_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import DEBUG_AFTER_THIS_VERBOSITY_LEVEL
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.api.irradiance.efficiency import calculate_pv_efficiency_time_series
from pvgisprototype.constants import IRRADIANCE_UNITS
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
from pvgisprototype.constants import ALGORITHM_COLUMN_NAME
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
from pvgisprototype.cli.messages import WARNING_OUT_OF_RANGE_VALUES
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype import PhotovoltaicPower
from pandas import DatetimeIndex
from pvgisprototype import SurfaceTilt
from pvgisprototype.validation.hashing import generate_hash
from pvgisprototype.api.irradiance.photovoltaic_module import PhotovoltaicModuleModel


@log_function_call
def calculate_photovoltaic_power_output_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: Optional[DatetimeIndex] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    periods: Optional[int] = None,
    frequency: Optional[str] = TIMESTAMPS_FREQUENCY_DEFAULT,
    timezone: Optional[str] = None,
    random_time_series: bool = False,
    global_horizontal_irradiance: Optional[Path] = None,
    direct_horizontal_irradiance: Optional[Path] = None,
    spectral_factor=None,
    temperature_series: np.ndarray = np.array(TEMPERATURE_DEFAULT),
    wind_speed_series: np.ndarray = np.array(WIND_SPEED_DEFAULT),
    mask_and_scale: bool = False,
    neighbor_lookup: MethodsForInexactMatches = None,
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    in_memory: bool = False,
    dtype: str = DATA_TYPE_DEFAULT,
    array_backend: str = ARRAY_BACKEND_DEFAULT,
    multi_thread: bool = True,
    surface_orientation: Optional[float] = SURFACE_ORIENTATION_DEFAULT,
    surface_tilt: Optional[SurfaceTilt] = SURFACE_TILT_DEFAULT,
    linke_turbidity_factor_series: LinkeTurbidityFactor = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Optional[bool] = True,
    refracted_solar_zenith: Optional[float] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Optional[float] = ALBEDO_DEFAULT,
    apply_angular_loss_factor: Optional[bool] = True,
    solar_position_model: SolarPositionModel = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModel = SolarIncidenceModel.jenco,
    solar_time_model: SolarTimeModel = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: str = "minutes",
    angle_units: str = RADIANS,
    angle_output_units: str = RADIANS,
    # horizon_heights: List[float] = None,
    photovoltaic_module: PhotovoltaicModuleModel = PHOTOVOLTAIC_MODULE_DEFAULT, #PhotovoltaicModuleModel.CSI_FREE_STANDING, 
    system_efficiency: Optional[float] = SYSTEM_EFFICIENCY_DEFAULT,
    power_model: PVModuleEfficiencyAlgorithm = None,
    temperature_model: ModuleTemperatureAlgorithm = None,
    efficiency: Optional[float] = None,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
    log: int = 0,
    fingerprint: bool = False,
    profile: bool = False, 
):
    """
    Estimate the photovoltaic power over a time series or an arbitrarily
    aggregated energy production of a PV system based on the effective solar
    irradiance incident on a solar surface, the ambient temperature and
    optionally wind speed.

    Parameters
    ----------
    longitude : float
        The longitude of the location for which the energy production is calculated.
    latitude : float
        The latitude of the location.
    elevation : float
        Elevation of the location in meters.
    timestamps : Optional[datetime], optional
        Specific timestamps for which to calculate the irradiance. Default is None.
    start_time : Optional[datetime], optional
        Start time for the calculation period. Default is None.
    frequency : Optional[str], optional
        Frequency for time series data generation. Default is None.
    end_time : Optional[datetime], optional
        End time for the calculation period. Default is None.
    timezone : Optional[str], optional
        Timezone of the location. Default is None.
    random_time_series : bool, default False
        If True, generates a random time series.
    global_horizontal_component : Optional[Path], optional
        Path to data file for global horizontal irradiance. Default is None.
    direct_horizontal_component : Optional[Path], optional
        Path to data file for direct horizontal irradiance. Default is None.
    temperature_series : TemperatureSeries
        Series of temperature values. Default is TEMPERATURE_DEFAULT.
    wind_speed_series : WindSpeedSeries
        Series of wind speed values. Default is WIND_SPEED_DEFAULT.
    mask_and_scale : bool, default False
        If True, applies masking and scaling to the input data.

    # ... other parameters ...

    Returns
    -------
    photovoltaic_power_output_series : ndarray
        Array of effective irradiance values.
    results : dict
        Dictionary containing detailed results of the calculation.
    title : str
        Title of the output data.

    Examples
    --------
    >>> calculate_photovoltaic_power_output_series(10.0, 20.0, 100.0, start_time="2023-01-01", end_time="2023-01-31")
    # This will return the effective irradiance series, results, and title for the specified parameters.

    Notes
    -----
    This function is part of the Typer-based CLI for the new PVGIS implementation in Python. It provides an interface for estimating the energy production of a photovoltaic system, taking into account various environmental and system parameters.
    """
    # import click
    # ctx = click.get_current_context()
    # print(f"args here : {ctx.args}")
    # print(f"Command here : {ctx.command}")
    # print(f"Command name here : {ctx.command.name}")
    # print(f"Command path here : {ctx.command_path}")
    # print(f"get_parameter_source() : {ctx.get_parameter_source('temperature_series')}")
    # print(f"get_usage() : {ctx.get_usage()}")
    # print(f"info_name : {ctx.info_name}")
    # print(f"invoked_subcommand : {ctx.invoked_subcommand}")
    # print(f"meta : {ctx.meta}")
    # print(f"obj : {ctx.obj}")
    # print(f"params : {ctx.params}")
    # print(f"parent : {ctx.parent}")
    # print()
    if profile:
        import cProfile
        pr = cProfile.Profile()
        pr.enable()

    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info('i [bold]Modelling[/bold] the [magenta]solar altitude[/magenta] for the given timestamps ..')
    solar_altitude_series = model_solar_altitude_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        # solar_time_model=solar_time_model,
        # time_offset_global=time_offset_global,
        # hour_offset=hour_offset,
        # perigee_offset=perigee_offset,
        # eccentricity_correction_factor=eccentricity_correction_factor,
        # time_output_units=time_output_units,
        # angle_units=angle_units,
        # angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(f'i [bold]Modelling[/bold] the [magenta]solar azimuth[/magenta] for the given timestamps ..')
    solar_azimuth_series = model_solar_azimuth_time_series(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        timezone=timezone,
        solar_position_model=solar_position_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        solar_time_model=solar_time_model,
        # time_offset_global=time_offset_global,
        # hour_offset=hour_offset,
        # perigee_offset=perigee_offset,
        # eccentricity_correction_factor=eccentricity_correction_factor,
        # time_output_units=time_output_units,
        # angle_units=angle_units,
        # angle_output_units=angle_output_units,
        dtype=dtype,
        array_backend=array_backend,
        verbose=verbose,
        log=log,
    )
    # Masks based on the solar altitude series
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(f'i [bold]Masking out[/bold] moments in time when [magenta]the surface is not illuminated [/magenta] ..')
    mask_above_horizon = solar_altitude_series.value > 0
    mask_low_angle = (solar_altitude_series.value >= 0) & (solar_altitude_series.value < 0.04)  # FIXME: Is the value 0.04 in radians or degrees ?
    mask_below_horizon = solar_altitude_series.value < 0
    in_shade = is_surface_in_shade_time_series(
            solar_altitude_series,
            solar_azimuth_series,
            )
    mask_not_in_shade = ~in_shade
    # mask_above_horizon_not_in_shade = np.logical_and.reduce(mask_above_horizon, mask_not_in_shade)
    mask_above_horizon_not_in_shade = np.logical_and(mask_above_horizon, mask_not_in_shade)

    # =======================================================================
    from pvgisprototype.validation.arrays import create_array
    shape_of_array = (
        solar_altitude_series.value.shape
    )  # Borrow shape from solar_altitude_series
    direct_irradiance_series = create_array(
        shape_of_array, dtype=dtype, init_method="zeros", backend=array_backend
    )
    diffuse_irradiance_series = create_array(
        shape_of_array, dtype=dtype, init_method="zeros", backend=array_backend
    )
    reflected_irradiance_series = create_array(
        shape_of_array, dtype=dtype, init_method="zeros", backend=array_backend
    )
    # =======================================================================

    # For very low sun angles
    direct_irradiance_series[mask_low_angle] = 0  # Direct radiation is negligible

    # For sun below the horizon
    direct_irradiance_series[mask_below_horizon] = 0
    diffuse_irradiance_series[mask_below_horizon] = 0
    reflected_irradiance_series[mask_below_horizon] = 0

    # For sun above horizon and not in shade
    if np.any(mask_above_horizon_not_in_shade):
        if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
            logger.info(f'i [bold]Calculating[/bold] the [magenta]direct inclined irradiance[/magenta] for moments not in shade ..')
        direct_irradiance_series[mask_above_horizon_not_in_shade] = (
            calculate_direct_inclined_irradiance_time_series_pvgis(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                timestamps=timestamps,
                start_time=start_time,
                end_time=end_time,
                timezone=timezone,
                random_time_series=random_time_series,
                direct_horizontal_component=direct_horizontal_irradiance,
                mask_and_scale=mask_and_scale,
                neighbor_lookup=neighbor_lookup,
                tolerance=tolerance,
                in_memory=in_memory,
                surface_tilt=surface_tilt,
                surface_orientation=surface_orientation,
                linke_turbidity_factor_series=linke_turbidity_factor_series,
                apply_atmospheric_refraction=apply_atmospheric_refraction,
                refracted_solar_zenith=refracted_solar_zenith,
                apply_angular_loss_factor=apply_angular_loss_factor,
                solar_position_model=solar_position_model,
                solar_incidence_model=solar_incidence_model,
                solar_time_model=solar_time_model,
                time_offset_global=time_offset_global,
                hour_offset=hour_offset,
                solar_constant=solar_constant,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                time_output_units=time_output_units,
                angle_units=angle_units,
                angle_output_units=angle_output_units,
                dtype=dtype,
                array_backend=array_backend,
                verbose=0,  # no verbosity here by choice!
                log=log,
            )
        )[mask_above_horizon_not_in_shade]

    # Calculate diffuse and reflected irradiance for sun above horizon
    if np.any(mask_above_horizon):
        if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
            logger.info(f'i [bold]Calculating[/bold] the [magenta]diffuse inclined irradiance[/magenta] for daylight moments ..')
        diffuse_irradiance_series[
            mask_above_horizon
        ] = calculate_diffuse_inclined_irradiance_time_series(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            timestamps=timestamps,
            start_time=start_time,
            end_time=end_time,
            timezone=timezone,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            refracted_solar_zenith=refracted_solar_zenith,
            global_horizontal_component=global_horizontal_irradiance,
            direct_horizontal_component=direct_horizontal_irradiance,  # time series, optional
            apply_angular_loss_factor=apply_angular_loss_factor,
            solar_position_model=solar_position_model,
            solar_time_model=solar_time_model,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
            neighbor_lookup=neighbor_lookup,
            dtype=dtype,
            array_backend=array_backend,
            multi_thread=multi_thread,
            verbose=0,  # no verbosity here by choice!
            log=log,
        )[
            mask_above_horizon
        ]
        if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
            logger.info(f'i [bold]Calculating[/bold] the [magenta]reflected inclined irradiance[/magenta] for daylight moments ..')
        reflected_irradiance_series[
            mask_above_horizon
        ] = calculate_ground_reflected_inclined_irradiance_time_series(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            timestamps=timestamps,
            start_time=start_time,
            end_time=end_time,
            timezone=timezone,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            linke_turbidity_factor_series=linke_turbidity_factor_series,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            refracted_solar_zenith=refracted_solar_zenith,
            albedo=albedo,
            direct_horizontal_component=direct_horizontal_irradiance,  # time series, optional
            apply_angular_loss_factor=apply_angular_loss_factor,
            solar_position_model=solar_position_model,
            solar_time_model=solar_time_model,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            solar_constant=solar_constant,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
            dtype=dtype,
            array_backend=array_backend,
            verbose=0,  # no verbosity here by choice!
            log=log,
        )[
            mask_above_horizon
        ]

    # sum components
    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(f'\ni [bold]Calculating[/bold] the [magenta]global inclined irradiance[/magenta] ..')
    global_irradiance_series = (
        direct_irradiance_series
        + diffuse_irradiance_series
        + reflected_irradiance_series
    )
    # -----------------------------------------------------------------------
    # Try the following, to deduplicate code,
    # global_irradiance_series = calculate_global_irradiance_time_series()
    # ?
    # -----------------------------------------------------------------------
    if not power_model:
        if not efficiency:  # user-set  -- RenameMe ?  FIXME
            # print(f'Using preset system efficiency {system_efficiency}')
            efficiency_coefficient_series = system_efficiency
        else:
            # print(f'Efficiency set to {efficiency}')
            efficiency_coefficient_series = efficiency
    else:
        if not efficiency:
            from pvgisprototype.api.series.select import select_time_series
            from pvgisprototype.constants import DEGREES
            from pvgisprototype import TemperatureSeries
            if isinstance(temperature_series, Path):
                temperature_series = TemperatureSeries(
                        value=select_time_series(
                            time_series=temperature_series,
                            # longitude=longitude_for_selection,
                            # latitude=latitude_for_selection,
                            longitude=convert_float_to_degrees_if_requested(longitude, DEGREES),
                            latitude=convert_float_to_degrees_if_requested(latitude, DEGREES),
                            timestamps=timestamps,
                            start_time=start_time,
                            end_time=end_time,
                            # convert_longitude_360=convert_longitude_360,
                            neighbor_lookup=neighbor_lookup,
                            tolerance=tolerance,
                            mask_and_scale=mask_and_scale,
                            in_memory=in_memory,
                            verbose=0,  # no verbosity here by choice!
                            log=log,
                            ).to_numpy().astype(dtype=dtype),
                        unit=TEMPERATURE_UNIT)
            efficiency_coefficient_series = calculate_pv_efficiency_time_series(
                spectral_factor=spectral_factor,
                irradiance_series=global_irradiance_series,
                temperature_series=temperature_series,
                # model_constants=EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT,
                photovoltaic_module=photovoltaic_module,
                standard_test_temperature=TEMPERATURE_DEFAULT,
                wind_speed_series=wind_speed_series,
                power_model=power_model,
                temperature_model=temperature_model,
                dtype=dtype,
                array_backend=array_backend,
                verbose=0,  # no verbosity here by choice!
                log=log,
            )
            efficiency_coefficient_series *= system_efficiency  # on-top-of !

    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(f'i [bold]Applying[/bold] some [magenta]efficiency coefficients[/magenta] on the global inclined irradiance ..')
    photovoltaic_power_output_series = global_irradiance_series * efficiency_coefficient_series

    if verbose > HASH_AFTER_THIS_VERBOSITY_LEVEL:
        logger.info(f'i [bold]Building the output[/bold] ..')

    components_container = {
        'main': lambda: {
            TITLE_KEY_NAME: PHOTOVOLTAIC_POWER,
            PHOTOVOLTAIC_POWER_COLUMN_NAME: photovoltaic_power_output_series,
        },# if verbose > 0 else {},
        
        'extended': lambda: {
            TITLE_KEY_NAME: PHOTOVOLTAIC_POWER + " & in-plane components",
            EFFICIENCY_COLUMN_NAME: efficiency_coefficient_series,
            ALGORITHM_COLUMN_NAME: power_model.value if power_model else NOT_AVAILABLE,
            GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME: global_irradiance_series,
            DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME: direct_irradiance_series,
            DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME: diffuse_irradiance_series,
            REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME: reflected_irradiance_series,
        } if verbose > 1 else {},
        
        'more_extended': lambda: {
            EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME: direct_irradiance_series * efficiency_coefficient_series,
            EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME: diffuse_irradiance_series * efficiency_coefficient_series,
            EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME: reflected_irradiance_series * efficiency_coefficient_series,
        } if verbose > 2 else {},
        
        'even_more_extended': lambda: {
            # DIRECT_HORIZONTAL_IRRADIANCE_COLUMN_NAME:
            # DIFFUSE_HORIZONTAL_IRRADIANCE_COLUMN_NAME: 
            # REFLECTED_HORIZONTAL_IRRADIANCE_COLUMN_NAME:
            TEMPERATURE_COLUMN_NAME: temperature_series.value,
            WIND_SPEED_COLUMN_NAME: NOT_AVAILABLE,
        } if verbose > 3 else {},
        
        'and_even_more_extended': lambda: {
            SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(surface_orientation, angle_output_units),
            SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(surface_tilt, angle_output_units),
            ABOVE_HORIZON_COLUMN_NAME: mask_above_horizon,
            LOW_ANGLE_COLUMN_NAME: mask_low_angle,
            BELOW_HORIZON_COLUMN_NAME: mask_below_horizon,
            SHADE_COLUMN_NAME: in_shade,
        } if verbose > 4 else {},
        
        'extra': lambda: {
            INCIDENCE_ALGORITHM_COLUMN_NAME: solar_incidence_model,
            ALTITUDE_COLUMN_NAME: solar_altitude_series,
            AZIMUTH_COLUMN_NAME: solar_azimuth_series,
        } if verbose > 5 else {},

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
        import pstats
        import io
        pr.disable()

        # write profiling statistics to file
        profile_filename = "profiling_stats.prof"
        pr.dump_stats(profile_filename)
        print(f"Profiling stats saved to {profile_filename}")

        s = io.StringIO()
        sortby = pstats.SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()

        if verbose > 6:
            print(s.getvalue())

    log_data_fingerprint(
            data=photovoltaic_power_output_series,
            log_level=log,
            hash_after_this_verbosity_level=HASH_AFTER_THIS_VERBOSITY_LEVEL,
    )
    return PhotovoltaicPower(
            value=photovoltaic_power_output_series,
            unit=POWER_UNIT,
            position_algorithm="",
            timing_algorithm="",
            elevation=elevation,
            surface_orientation=surface_orientation,
            surface_tilt=surface_tilt,
            irradiance=global_irradiance_series,
            components=components,
            )
