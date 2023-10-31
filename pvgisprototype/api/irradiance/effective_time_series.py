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
from pvgisprototype.validation.functions import ModelSolarPositionInputModel
from pvgisprototype.api.geometry.models import SolarDeclinationModels
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.geometry.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.utilities.conversions import convert_to_radians
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours_time_series
from pvgisprototype.api.irradiance.direct import SolarIncidenceModels
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithms
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.api.irradiance.direct_time_series import print_irradiance_table_2
from pvgisprototype.api.irradiance.direct_time_series import calculate_direct_inclined_irradiance_time_series_pvgis
from pvgisprototype.api.irradiance.diffuse_time_series import calculate_diffuse_inclined_irradiance_time_series
from pvgisprototype.api.irradiance.reflected_time_series import calculate_ground_reflected_inclined_irradiance_time_series
from pvgisprototype.api.geometry.solar_incidence_time_series import model_solar_incidence_time_series
from pvgisprototype.api.geometry.solar_altitude_time_series import model_solar_altitude_time_series
from pvgisprototype.api.geometry.solar_time_time_series import model_solar_time_time_series
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.cli.csv import write_irradiance_csv
from pvgisprototype.constants import TEMPERATURE_DEFAULT
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
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.api.irradiance.efficiency_time_series import calculate_pv_efficiency_time_series
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.constants import RADIANS
from pvgisprototype.constants import EFFECTIVE_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import EFFICIENCY_COLUMN_NAME
from pvgisprototype.constants import ALGORITHM_COLUMN_NAME
from pvgisprototype.constants import GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME
from pvgisprototype.constants import SURFACE_TILT_COLUMN_NAME
from pvgisprototype.constants import SURFACE_ORIENTATION_COLUMN_NAME
from pvgisprototype.constants import ABOVE_HORIZON_COLUMN_NAME
from pvgisprototype.constants import LOW_ANGLE_COLUMN_NAME
from pvgisprototype.constants import BELOW_HORIZON_COLUMN_NAME
# from pvgisprototype.constants import TEMPERATURE_COLUMN_NAME
# from pvgisprototype.constants import WIND_SPEED_COLUMN_NAME
# from pvgisprototype.constants import SHADE


def is_surface_in_shade_time_series(input_array, threshold=10):
    """
    Determine if a surface is in shade based on solar altitude for each timestamp.

    Parameters:
    - solar_altitude_series_array (numpy array): Array of solar altitude angles for each timestamp.
    - shade_threshold (float): Solar altitude angle below which the surface is considered to be in shade.

    Returns:
    - numpy array: Boolean array indicating whether the surface is in shade at each timestamp.
    """
    # return solar_altitude_series_array < threshold
    return np.full(input_array.size, False)


# @app.callback(
#     'effective-time-series',
#    invoke_without_command=True,
#    no_args_is_help=True,
#    # context_settings={"ignore_unknown_options": True},
#    help=f'Calculate the clear-sky ground reflected irradiance',
# )
def calculate_effective_irradiance_time_series(
    longitude: float,
    latitude: float,
    elevation: float,
    timestamps: Optional[datetime] = None,
    start_time: Optional[datetime] = None,
    frequency: Optional[str] = None,
    end_time: Optional[datetime] = None,
    timezone: Optional[str] = None,
    random_time_series: bool = False,
    global_horizontal_component: Optional[Path] = None,
    direct_horizontal_component: Optional[Path] = None,
    temperature_series: float = 25,
    wind_speed_series: float = 0,
    mask_and_scale: bool = False,
    neighbor_lookup: MethodsForInexactMatches = None,
    tolerance: Optional[float] = TOLERANCE_DEFAULT,
    in_memory: bool = False,
    surface_tilt: Optional[float] = SURFACE_TILT_DEFAULT,
    surface_orientation: Optional[float] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor_series: List[float] = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Optional[bool] = True,
    refracted_solar_zenith: Optional[float] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Optional[float] = 2,
    apply_angular_loss_factor: Optional[bool] = True,
    solar_position_model: SolarPositionModels = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: SolarIncidenceModels = SolarIncidenceModels.jenco,
    solar_time_model: SolarTimeModels = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: float = 0,
    hour_offset: float = 0,
    solar_constant: float = SOLAR_CONSTANT,
    perigee_offset: float = PERIGEE_OFFSET,
    eccentricity_correction_factor: float = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: str = 'minutes',
    angle_units: str = RADIANS,
    angle_output_units: str = RADIANS,
    # horizon_heights: List[float] = None,
    system_efficiency: Optional[float] = SYSTEM_EFFICIENCY_DEFAULT,
    efficiency_model: PVModuleEfficiencyAlgorithms = None,
    efficiency: Optional[float] = None,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    solar_altitude_series = model_solar_altitude_time_series(
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
        verbose=0,
    )
    # Masks based on the solar altitude series
    mask_above_horizon = solar_altitude_series.value > 0
    mask_low_angle = (solar_altitude_series.value >= 0) & (solar_altitude_series.value < 0.04)      # FIXME: Is this in radians or degrees ?
    mask_below_horizon = solar_altitude_series.value < 0
    in_shade = is_surface_in_shade_time_series(solar_altitude_series.value)
    mask_not_in_shade = ~in_shade
    mask_above_horizon_not_shade = np.logical_and.reduce((mask_above_horizon, mask_not_in_shade))

    # Initialize arrays with zeros
    direct_irradiance_series = np.zeros_like(solar_altitude_series.value, dtype='float64')
    diffuse_irradiance_series = np.zeros_like(solar_altitude_series.value, dtype='float64')
    reflected_irradiance_series = np.zeros_like(solar_altitude_series.value, dtype='float64')

    # For very low sun angles
    direct_irradiance_series[mask_low_angle] = 0  # Direct radiation is negligible

    # For sun below the horizon
    direct_irradiance_series[mask_below_horizon] = 0
    diffuse_irradiance_series[mask_below_horizon] = 0
    reflected_irradiance_series[mask_below_horizon] = 0

    # For sun above horizon and not in shade
    if np.any(mask_above_horizon_not_shade):
        direct_irradiance_series[mask_above_horizon_not_shade] = (
            calculate_direct_inclined_irradiance_time_series_pvgis(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                timestamps=timestamps,
                start_time=start_time,
                end_time=end_time,
                timezone=timezone,
                random_time_series=random_time_series,
                direct_horizontal_component=direct_horizontal_component,
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
                verbose=0,  # no verbosity here by choice!
            )
        )[mask_above_horizon_not_shade]

    # Calculate diffuse and reflected irradiance for sun above horizon
    if np.any(mask_above_horizon):
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
            global_horizontal_component=global_horizontal_component,
            direct_horizontal_component=direct_horizontal_component,  # time series, optional
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
            verbose=0,  # no verbosity here by choice!
        )[
            mask_above_horizon
        ]
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
            direct_horizontal_component=direct_horizontal_component,  # time series, optional
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
            verbose=0,  # no verbosity here by choice!
        )[
            mask_above_horizon
        ]

    # sum components
    global_irradiance_series = (
        direct_irradiance_series
        + diffuse_irradiance_series
        + reflected_irradiance_series
    )

    if not efficiency_model:
        if not efficiency:
            # print(f'Using preset system efficiency {system_efficiency}')
            efficiency_coefficient_series = system_efficiency
        else:
            # print(f'Efficiency set to {efficiency}')
            efficiency_coefficient_series = efficiency
    else:
        if not efficiency:
            # print(f'Using PV module efficiency algorithm {efficiency_model}')
            efficiency_coefficient_series = calculate_pv_efficiency_time_series(
                irradiance_series=global_irradiance_series,
                temperature_series=temperature_series,
                model_constants=EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT,
                standard_test_temperature=TEMPERATURE_DEFAULT,
                wind_speed_series=wind_speed_series,
                model=efficiency_model,
                verbose=0,  # no verbosity here by choice!
            )

    effective_irradiance_series = (
        global_irradiance_series * efficiency_coefficient_series
    )

    # Reporting --------------------------------------------------------------

    results = {
        EFFECTIVE_IRRADIANCE_COLUMN_NAME: effective_irradiance_series,
    }
    title = 'Effective'
    
    if verbose > 2:
        more_extended_results = {
            # "Global*": global_irradiance_series * efficiency_coefficient_series,
            EFFECTIVE_DIRECT_IRRADIANCE_COLUMN_NAME: direct_irradiance_series * efficiency_coefficient_series,
            EFFECTIVE_DIFFUSE_IRRADIANCE_COLUMN_NAME: diffuse_irradiance_series * efficiency_coefficient_series,
            EFFECTIVE_REFLECTED_IRRADIANCE_COLUMN_NAME: reflected_irradiance_series * efficiency_coefficient_series,
            # "Shade": in_shade,
        }
        results = results | more_extended_results

    if verbose > 1:
        extended_results = {
            EFFICIENCY_COLUMN_NAME: efficiency_coefficient_series,
            ALGORITHM_COLUMN_NAME: efficiency_model.value if efficiency_model else NOT_AVAILABLE,
            GLOBAL_INCLINED_IRRADIANCE_COLUMN_NAME: global_irradiance_series,
            DIRECT_INCLINED_IRRADIANCE_COLUMN_NAME: direct_irradiance_series,
            DIFFUSE_INCLINED_IRRADIANCE_COLUMN_NAME: diffuse_irradiance_series,
            REFLECTED_INCLINED_IRRADIANCE_COLUMN_NAME: reflected_irradiance_series,
        }
        results = results | extended_results
        title += ' & in-plane components'

    if verbose > 3:
        even_more_extended_results = {
            # TEMPERATURE_COLUMN_NAME: temperature_series,          # FIXME: Not defined
            # WIND_SPEED_COLUMN_NAME: wind_speed_series,          # FIXME: Not defined
        }
        results = results | even_more_extended_results

    if verbose > 4:
        and_even_more_extended_results = {
            SURFACE_TILT_COLUMN_NAME: convert_float_to_degrees_if_requested(surface_tilt, angle_output_units),
            SURFACE_ORIENTATION_COLUMN_NAME: convert_float_to_degrees_if_requested(surface_orientation, angle_output_units),
            ABOVE_HORIZON_COLUMN_NAME: mask_above_horizon,
            LOW_ANGLE_COLUMN_NAME: mask_low_angle,
            BELOW_HORIZON_COLUMN_NAME: mask_below_horizon,
            # SHADE: in_shade,                               # FIXME: Not defined
        }
        results = results | and_even_more_extended_results

    if verbose == 6:
        results = {
            EFFECTIVE_IRRADIANCE_COLUMN_NAME: effective_irradiance_series,
        }
        title = 'Effective'
        longitude = latitude = None

    if verbose > 6:
        debug(locals())

    return effective_irradiance_series, results, title
