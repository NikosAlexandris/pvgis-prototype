from devtools import debug
from pathlib import Path
from math import cos
from typing import Annotated
from typing import List
from typing import Optional
import math
import numpy as np
import typer
from enum import Enum
from rich import print


from datetime import datetime
from pvgisprototype.validation.functions import ModelSolarPositionInputModel
from pvgisprototype.api.geometry.models import SolarDeclinationModels
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.utilities.conversions import convert_to_radians
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours_time_series
from pvgisprototype.api.irradiance.direct import SolarIncidenceModels
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithms
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_geometry_surface
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_time
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_efficiency
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_atmospheric_properties
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_earth_orbit
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output

from pvgisprototype.api.irradiance.direct_time_series import print_irradiance_table_2
from pvgisprototype.api.irradiance.direct_time_series import calculate_direct_inclined_irradiance_time_series_pvgis
from pvgisprototype.api.irradiance.diffuse_time_series import calculate_diffuse_inclined_irradiance_time_series
from pvgisprototype.api.irradiance.reflected_time_series import calculate_ground_reflected_inclined_irradiance_time_series
from pvgisprototype.api.geometry.solar_incidence_time_series import model_solar_incidence_time_series
from pvgisprototype.api.geometry.solar_altitude_time_series import model_solar_altitude_time_series
from pvgisprototype.api.geometry.solar_time_time_series import model_solar_time_time_series
from pvgisprototype.api.series.statistics import calculate_series_statistics
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.api.series.statistics import export_statistics_to_csv
from pvgisprototype.cli.csv import write_irradiance_csv
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_frequency
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_global_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_temperature_time_series
from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_argument_wind_speed_time_series
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer_parameters import typer_option_inexact_matches_method
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.typer_parameters import typer_argument_surface_tilt
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_argument_surface_orientation
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor
from pvgisprototype.constants import LINKE_TURBIDITY_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_albedo
from pvgisprototype.constants import ALBEDO_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer_parameters import typer_option_solar_incidence_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.constants import TIME_OFFSET_GLOBAL_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.constants import HOUR_OFFSET_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_solar_constant
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_argument_horizon_heights
from pvgisprototype.cli.typer_parameters import typer_option_system_efficiency
from pvgisprototype.constants import SYSTEM_EFFICIENCY_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_efficiency
from pvgisprototype.constants import EFFICIENCY_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_pv_module_efficiency_algorithm
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.api.irradiance.efficiency_time_series import calculate_pv_efficiency_time_series
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import NOT_AVAILABLE


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Estimate the effective irradiance incident on a surface over a time series ",
)


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


@app.callback(
    'effective-time-series',
   invoke_without_command=True,
   no_args_is_help=True,
   # context_settings={"ignore_unknown_options": True},
   help=f'Calculate the clear-sky ground reflected irradiance',
)
def calculate_effective_irradiance_time_series(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamps: Annotated[Optional[datetime], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    frequency: Annotated[Optional[str], typer_option_frequency] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    random_time_series: bool = False,
    global_horizontal_component: Annotated[Optional[Path], typer_option_global_horizontal_irradiance] = None,
    direct_horizontal_component: Annotated[Optional[Path], typer_option_direct_horizontal_irradiance] = None,
    temperature_series: Annotated[float, typer_argument_temperature_time_series] = 25,
    wind_speed_series: Annotated[float, typer_argument_wind_speed_time_series] = 0,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodsForInexactMatches, typer_option_nearest_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = 45,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = 180,
    linke_turbidity_factor_series: Annotated[List[float], typer_option_linke_turbidity_factor_series] = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = 1.5853349194640094,  # radians
    albedo: Annotated[Optional[float], typer_option_albedo] = 2,
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_position_model: Annotated[SolarPositionModels, typer_option_solar_position_model] = SolarPositionModels.noaa,
    solar_incidence_model: Annotated[SolarIncidenceModels, typer_option_solar_incidence_model] = SolarIncidenceModels.jenco,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.noaa,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    # horizon_heights: Annotated[List[float], typer.Argument(help="Array of horizon elevations.")] = None,
    system_efficiency: Annotated[Optional[float], typer_option_system_efficiency] = SYSTEM_EFFICIENCY_DEFAULT,
    efficiency_model: Annotated[PVModuleEfficiencyAlgorithms, typer_option_pv_module_efficiency_algorithm] = None,
    efficiency: Annotated[Optional[float], typer_option_efficiency] = None,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = 'series_in',
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
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
    solar_altitude_series_array = np.array([x.value for x in solar_altitude_series])

    # Masks based on the solar altitude series
    mask_above_horizon = solar_altitude_series_array > 0
    mask_low_angle = (solar_altitude_series_array >= 0) & (solar_altitude_series_array < 0.04)
    mask_below_horizon = solar_altitude_series_array < 0
    in_shade = is_surface_in_shade_time_series(solar_altitude_series_array)
    mask_not_in_shade = ~in_shade
    mask_above_horizon_not_shade = np.logical_and.reduce((mask_above_horizon, mask_not_in_shade))

    # Initialize arrays with zeros
    direct_irradiance_series = np.zeros_like(solar_altitude_series, dtype='float64')
    diffuse_irradiance_series = np.zeros_like(solar_altitude_series, dtype='float64')
    reflected_irradiance_series = np.zeros_like(solar_altitude_series, dtype='float64')

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
        "Effective": effective_irradiance_series,
    }
    title = 'Effective'
    
    if verbose > 2:
        more_extended_results = {
            # "Global*": global_irradiance_series * efficiency_coefficient_series,
            "Direct*": direct_irradiance_series * efficiency_coefficient_series,
            "Diffuse*": diffuse_irradiance_series * efficiency_coefficient_series,
            "Reflected*": reflected_irradiance_series * efficiency_coefficient_series,
            # "Shade": in_shade,
        }
        results = results | more_extended_results

    if verbose > 1:
        extended_results = {
            "Efficiency": efficiency_coefficient_series,
            "Algorithm": efficiency_model.value if efficiency_model else NOT_AVAILABLE,
            "Global": global_irradiance_series,
            "Direct": direct_irradiance_series,
            "Diffuse": diffuse_irradiance_series,
            "Reflected": reflected_irradiance_series,
        }
        results = results | extended_results
        title += ' & in-plane components'

    if verbose > 3:
        even_more_extended_results = {
            "Temperature": temperature_series,
            "Wind speed": wind_speed_series,
        }
        results = results | even_more_extended_results

    if verbose > 4:
        and_even_more_extended_results = {
            "Tilt": convert_float_to_degrees_if_requested(surface_tilt, angle_output_units),
            "🧭 Orientation": convert_float_to_degrees_if_requested(surface_orientation, angle_output_units),
            "Above horizon": mask_above_horizon,
            "Low angle": mask_low_angle,
            "Below horizon": mask_below_horizon,
            "Shade": in_shade,
        }
        results = results | and_even_more_extended_results

    if verbose == 7:
        results = {
            "Effective": effective_irradiance_series,
        }
        title = 'Effective'
        longitude = latitude = None

    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)

    if verbose > 5:
        debug(locals())

    print_irradiance_table_2(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        dictionary=results,
        title=title + f' irradiance series {IRRADIANCE_UNITS}',
        rounding_places=rounding_places,
        verbose=verbose,
    )

    import xarray as xr
    effective_irradiance_data_array = xr.DataArray(
        effective_irradiance_series,
        coords=[('time', timestamps)],
        name='Effective irradiance series'
    )
    effective_irradiance_data_array.attrs['units'] = 'W/m^2'
    effective_irradiance_data_array.attrs['long_name'] = 'Effective Solar Irradiance'

    if statistics:
        data_statistics = calculate_series_statistics(effective_irradiance_data_array)
        print_series_statistics(data_statistics)

    if csv:
        write_irradiance_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=results,
            filename=csv,
        )

    return effective_irradiance_series
