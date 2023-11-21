from .rich_help_panel_names import rich_help_panel_series_irradiance
from .rich_help_panel_names import rich_help_panel_toolbox
from click import Context
from datetime import datetime
from devtools import debug
from enum import Enum
from math import cos
from pathlib import Path
from pvgisprototype.api.geometry.models import SOLAR_POSITION_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SOLAR_TIME_ALGORITHM_DEFAULT
from pvgisprototype.api.geometry.models import SolarDeclinationModels
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from pvgisprototype.api.geometry.solar_altitude_time_series import model_solar_altitude_time_series
from pvgisprototype.api.geometry.solar_incidence_time_series import model_solar_incidence_time_series
from pvgisprototype.api.geometry.solar_time_time_series import model_solar_time_time_series
from pvgisprototype.api.irradiance.diffuse import app as diffuse_irradiance
from pvgisprototype.api.irradiance.diffuse_time_series import app as diffuse_irradiance_series
from pvgisprototype.api.irradiance.diffuse_time_series import calculate_diffuse_inclined_irradiance_time_series
from pvgisprototype.api.irradiance.direct import SolarIncidenceModels
from pvgisprototype.api.irradiance.direct import app as direct_irradiance
from pvgisprototype.cli.irradiance_direct import app as direct_irradiance_series
from pvgisprototype.api.irradiance.direct_time_series import calculate_direct_inclined_irradiance_time_series_pvgis
from pvgisprototype.api.irradiance.direct_time_series import print_irradiance_table_2
from pvgisprototype.api.irradiance.effective_time_series import calculate_effective_irradiance_time_series
from pvgisprototype.api.irradiance.efficiency import app as pv_efficiency
from pvgisprototype.api.irradiance.efficiency_coefficients import EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT
from pvgisprototype.api.irradiance.efficiency_time_series import app as pv_efficiency_series
from pvgisprototype.api.irradiance.extraterrestrial import app as extraterrestrial_irradiance
from pvgisprototype.api.irradiance.extraterrestrial_time_series import app as extraterrestrial_irradiance_series
from pvgisprototype.api.irradiance.global_time_series import app as global_irradiance_series
from pvgisprototype.api.irradiance.limits import app as limits
from pvgisprototype.api.irradiance.loss import app as angular_loss_factor
from pvgisprototype.api.irradiance.models import MethodsForInexactMatches
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithms
from pvgisprototype.api.irradiance.reflected import app as reflected_irradiance
from pvgisprototype.api.irradiance.reflected_time_series import app as reflected_irradiance_series
from pvgisprototype.api.irradiance.reflected_time_series import calculate_ground_reflected_inclined_irradiance_time_series
from pvgisprototype.api.irradiance.shortwave import app as global_irradiance  # global is a Python reserved keyword!
from pvgisprototype.api.series.statistics import print_series_statistics
from pvgisprototype.api.utilities.conversions import convert_float_to_degrees_if_requested
from pvgisprototype.api.utilities.conversions import convert_to_radians
from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours_time_series
from pvgisprototype.cli.csv import write_irradiance_csv
from pvgisprototype.cli.messages import NOT_IMPLEMENTED_CLI
from pvgisprototype.cli.messages import TO_MERGE_WITH_SINGLE_VALUE_COMMAND
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_atmospheric_properties
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_earth_orbit
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_efficiency
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_geometry_surface
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_time
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_horizon_heights
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_surface_orientation
from pvgisprototype.cli.typer_parameters import typer_argument_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_argument_temperature_time_series
from pvgisprototype.cli.typer_parameters import typer_argument_timestamps
from pvgisprototype.cli.typer_parameters import typer_argument_wind_speed_time_series
from pvgisprototype.cli.typer_parameters import typer_option_albedo
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_csv
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer_parameters import typer_option_efficiency
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_frequency
from pvgisprototype.cli.typer_parameters import typer_option_groupby
from pvgisprototype.cli.typer_parameters import typer_option_global_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.cli.typer_parameters import typer_option_inexact_matches_method
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor_series
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.cli.typer_parameters import typer_option_nearest_neighbor_lookup
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.cli.typer_parameters import typer_option_pv_module_efficiency_algorithm
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_solar_constant
from pvgisprototype.cli.typer_parameters import typer_option_solar_incidence_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_statistics
from pvgisprototype.cli.typer_parameters import typer_option_surface_orientation
from pvgisprototype.cli.typer_parameters import typer_option_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_option_system_efficiency
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.cli.typer_parameters import typer_option_index
from pvgisprototype.constants import ALBEDO_DEFAULT
from pvgisprototype.constants import ANGLE_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import ATMOSPHERIC_REFRACTION_FLAG_DEFAULT
from pvgisprototype.constants import ECCENTRICITY_CORRECTION_FACTOR
from pvgisprototype.constants import EFFICIENCY_DEFAULT
from pvgisprototype.constants import HOUR_OFFSET_DEFAULT
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT
from pvgisprototype.constants import IRRADIANCE_UNITS
from pvgisprototype.constants import LINKE_TURBIDITY_DEFAULT
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.constants import NOT_AVAILABLE
from pvgisprototype.constants import PERIGEE_OFFSET
from pvgisprototype.constants import REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.constants import SURFACE_ORIENTATION_DEFAULT
from pvgisprototype.constants import SURFACE_TILT_DEFAULT
from pvgisprototype.constants import SYSTEM_EFFICIENCY_DEFAULT
from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype.constants import TIME_OFFSET_GLOBAL_DEFAULT
from pvgisprototype.constants import TIME_OUTPUT_UNITS_DEFAULT
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype.validation.functions import ModelSolarPositionInputModel
from rich import print
from typer.core import TyperGroup
from typing import Annotated
from typing import List
from typing import Optional
from typing_extensions import Annotated
import math
import numpy as np
import typer
from pvgisprototype import LinkeTurbidityFactor


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    # help=f":sun_with_face: Estimate the solar irradiance incident on a horizontal or inclined surface",
    help=f":sun_with_face: Estimate the solar irradiance incident on a solar surface",
)
# app.add_typer(
#     effective_irradiance,
#     name="effective",
#     help="Estimate the effective irradiance for a specific hour",
#     no_args_is_help=True,
#     rich_help_panel=rich_help_panel_series_irradiance,
# )
# app.add_typer(
#     effective_irradiance_series,
#     name="effective-series",
#     help="Estimate the effective irradiance over a time series",
#     no_args_is_help=True,
#     rich_help_panel=rich_help_panel_series_irradiance,
# )
@app.command(
    'effective',
    no_args_is_help=True,
    help=f"Estimate the effective irradiance incident on a surface over a time series ",
    rich_help_panel=rich_help_panel_series_irradiance,
)
def calculate_effective_irradiance(
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
    surface_tilt: Annotated[Optional[float], typer_option_surface_tilt] = SURFACE_TILT_DEFAULT,
    surface_orientation: Annotated[Optional[float], typer_option_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor_series: Annotated[LinkeTurbidityFactor, typer_option_linke_turbidity_factor_series] = None,  # Changed this to np.ndarray
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Annotated[Optional[float], typer_option_albedo] = 2,
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_position_model: Annotated[SolarPositionModels, typer_option_solar_position_model] = SOLAR_POSITION_ALGORITHM_DEFAULT,
    solar_incidence_model: Annotated[SolarIncidenceModels, typer_option_solar_incidence_model] = SolarIncidenceModels.jenco,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SOLAR_TIME_ALGORITHM_DEFAULT,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    # horizon_heights: Annotated[List[float], typer.Argument(help="Array of horizon elevations.")] = None,
    system_efficiency: Annotated[Optional[float], typer_option_system_efficiency] = SYSTEM_EFFICIENCY_DEFAULT,
    efficiency_model: Annotated[PVModuleEfficiencyAlgorithms, typer_option_pv_module_efficiency_algorithm] = None,
    efficiency: Annotated[Optional[float], typer_option_efficiency] = None,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    statistics: Annotated[bool, typer_option_statistics] = False,
    groupby: Annotated[Optional[str], typer_option_groupby] = None,
    csv: Annotated[Path, typer_option_csv] = None,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
    index: Annotated[bool, typer_option_index] = False,
):
    effective_irradiance_series, results, title = calculate_effective_irradiance_time_series(
        longitude=longitude,
        latitude=latitude,
        elevation=elevation,
        timestamps=timestamps,
        start_time=start_time,
        frequency=frequency,
        end_time=end_time,
        timezone=timezone,
        random_time_series=random_time_series,
        global_horizontal_component=global_horizontal_component,
        direct_horizontal_component=direct_horizontal_component,
        temperature_series=temperature_series,
        wind_speed_series=wind_speed_series,
        mask_and_scale=mask_and_scale,
        neighbor_lookup=neighbor_lookup,
        tolerance=tolerance,
        in_memory=in_memory,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        linke_turbidity_factor_series=linke_turbidity_factor_series,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        albedo=albedo,
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
        # horizon_heights=horizon_heights,
        system_efficiency=system_efficiency,
        efficiency_model=efficiency_model,
        efficiency=efficiency,
        verbose=verbose,
    )

    longitude = convert_float_to_degrees_if_requested(longitude, angle_output_units)
    latitude = convert_float_to_degrees_if_requested(latitude, angle_output_units)

    # if verbose > 5:
    #     debug(locals())

    print_irradiance_table_2(
        longitude=longitude,
        latitude=latitude,
        timestamps=timestamps,
        dictionary=results,
        title=title + f' irradiance series {IRRADIANCE_UNITS}',
        rounding_places=rounding_places,
        index=index,
        verbose=verbose,
    )
    if statistics:
        print_series_statistics(
            data_array=effective_irradiance_series,
            timestamps=timestamps,
            groupby=groupby,
            title="Effective irradiance",
        )
    if csv:
        write_irradiance_csv(
            longitude=longitude,
            latitude=latitude,
            timestamps=timestamps,
            dictionary=results,
            filename=csv,
        )
    if not verbose and not csv and not statistics:
        flat_list = effective_irradiance_series.flatten().astype(str)
        csv_str = ','.join(flat_list)
        print(csv_str)


app.add_typer(
    global_irradiance,
    name="global-single",
    help="Estimate the global irradiance for a specific hour",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    global_irradiance_series,
    name="global",
    help=f"Estimate the global irradiance over a time series {TO_MERGE_WITH_SINGLE_VALUE_COMMAND}",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    direct_irradiance,
    name="direct-single",
    help="Estimate the direct irradiance",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    direct_irradiance_series,
    name="direct",
    help=f'Estimate the direct irradiance over a period of time {TO_MERGE_WITH_SINGLE_VALUE_COMMAND}',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    diffuse_irradiance,
    name="diffuse-single",
    help="Estimate the diffuse irradiance",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    diffuse_irradiance_series,
    name="diffuse",
    help=f'Estimate the diffuse irradiance over a period of time {TO_MERGE_WITH_SINGLE_VALUE_COMMAND}',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    reflected_irradiance,
    name="reflected-single",
    help=f'Calculate the clear-sky ground reflected irradiance',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    reflected_irradiance_series,
    name="reflected",
    help=f'Calculate the clear-sky ground reflected irradiance over a period of time {TO_MERGE_WITH_SINGLE_VALUE_COMMAND}',
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_series_irradiance,
)
app.add_typer(
    extraterrestrial_irradiance,
    name="extraterrestrial-single",
    help="Calculate the extraterrestial irradiance for a day of the year",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    extraterrestrial_irradiance_series,
    name="extraterrestrial",
    help=f"Calculate the extraterrestial irradiance for a time series {TO_MERGE_WITH_SINGLE_VALUE_COMMAND}",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    angular_loss_factor,
    name="angular-loss",
    help=f"Estimate the angular loss factor for the direct horizontal irradiance {NOT_IMPLEMENTED_CLI}",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    pv_efficiency,
    name="pv-efficiency-single",
    no_args_is_help=True,
    # rich_help_panel=rich_help_panel_efficiency,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    pv_efficiency_series,
    name="pv-efficiency",
    no_args_is_help=True,
    # rich_help_panel=rich_help_panel_efficiency,
    rich_help_panel=rich_help_panel_toolbox,
)
app.add_typer(
    limits,
    name="limits",
    no_args_is_help=True,
    rich_help_panel=rich_help_panel_toolbox,
)
