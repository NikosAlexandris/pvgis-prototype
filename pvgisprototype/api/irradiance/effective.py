from devtools import debug
from pathlib import Path
from typing import Annotated
from typing import List
from typing import Optional
import numpy as np
import typer
from enum import Enum
from rich import print


from pvgisprototype.api.irradiance.direct import calculate_direct_inclined_irradiance_pvgis
# from pvgisprototype.api.irradiance.diffuse import calculate_diffuse_inclined_irradiance
# from pvgisprototype.api.irradiance.reflected import calculate_reflected_inclined_irradiance_pvgis

from datetime import datetime
# from pvgisprototype.validation.functions import ModelSolarPositionInputModel
from pvgisprototype.api.geometry.models import SolarDeclinationModels
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
# from pvgisprototype.api.utilities.conversions import convert_to_radians
# from pvgisprototype.api.utilities.timestamp import now_utc_datetimezone
# from pvgisprototype.api.utilities.timestamp import ctx_convert_to_timezone
# from pvgisprototype.api.utilities.timestamp import timestamp_to_decimal_hours
from pvgisprototype.api.irradiance.direct import SolarIncidenceModels
from pvgisprototype.api.irradiance.models import PVModuleEfficiencyAlgorithms
from pvgisprototype.constants import SOLAR_CONSTANT
# from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
# from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
# from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options
# from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_geometry_surface
# from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_time
# from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_efficiency
# from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_atmospheric_properties
# from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_earth_orbit
# from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output

from pvgisprototype.api.irradiance.diffuse import  calculate_diffuse_inclined_irradiance
from pvgisprototype.api.irradiance.reflected import  calculate_ground_reflected_inclined_irradiance
from pvgisprototype.api.geometry.solar_incidence import model_solar_incidence
from pvgisprototype.api.geometry.solar_declination import model_solar_declination
from pvgisprototype.api.geometry.solar_altitude import model_solar_altitude
from ..geometry.solar_time import model_solar_time
# from .direct import calculate_direct_horizontal_irradiance

from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_timestamp
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_timezone
# from pvgisprototype.cli.typer_parameters import typer_argument_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_option_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_temperature_time_series
from pvgisprototype.constants import TEMPERATURE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_argument_wind_speed_time_series
from pvgisprototype.constants import WIND_SPEED_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.constants import MASK_AND_SCALE_FLAG_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_inexact_matches_method
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.constants import TOLERANCE_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.constants import IN_MEMORY_FLAG_DEFAULT
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
from pvgisprototype.cli.typer_parameters import typer_option_solar_declination_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.constants import TIME_OFFSET_GLOBAL_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.constants import HOUR_OFFSET_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_solar_constant
from pvgisprototype.constants import SOLAR_CONSTANT
from pvgisprototype.cli.typer_parameters import typer_option_days_in_a_year
from pvgisprototype.constants import DAYS_IN_A_YEAR
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
# from pvgisprototype.constants import EFFICIENCY_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_pv_module_efficiency_algorithm
from pvgisprototype.constants import EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.constants import ROUNDING_PLACES_DEFAULT
from pvgisprototype.cli.typer_parameters import typer_option_verbose
from pvgisprototype.constants import VERBOSE_LEVEL_DEFAULT
from pvgisprototype.api.irradiance.efficiency import calculate_pv_efficiency


AOIConstants = []
AOIConstants.append(-0.074)
AOIConstants.append(0.155)


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Estimate the direct solar radiation",
)


class MethodsForInexactMatches(str, Enum):
    none = None # only exact matches
    pad = 'pad' # ffill: propagate last valid index value forward
    backfill = 'backfill' # bfill: propagate next valid index value backward
    nearest = 'nearest' # use nearest valid index value


def is_surface_in_shade():
    """
    """
    return False

    efficiency = pm / model_constants[0]

    # Check the output before returning
    if not np.isfinite(efficiency):
        raise ValueError("The computed efficiency is not a finite number.")
    elif not 0 <= efficiency <= 1:
        raise ValueError("The computed efficiency is not within the expected range (0 to 1).")


# @numba.jit(nopython=True)
@app.callback(
    'effective',
    invoke_without_command=True,
    no_args_is_help=True,
    # context_settings={"ignore_unknown_options": True},
    help="Estimate the effective irradiance for a specific hour",
)
def calculate_effective_irradiance(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    direct_horizontal_irradiance: Annotated[Optional[Path], typer_option_direct_horizontal_irradiance] = None,
    temperature: Annotated[float, typer_argument_temperature_time_series] = TEMPERATURE_DEFAULT,
    wind_speed: Annotated[float, typer_argument_wind_speed_time_series] = WIND_SPEED_DEFAULT,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = MASK_AND_SCALE_FLAG_DEFAULT,
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer_option_inexact_matches_method] = MethodsForInexactMatches.nearest,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = TOLERANCE_DEFAULT,
    in_memory: Annotated[bool, typer_option_in_memory] = IN_MEMORY_FLAG_DEFAULT,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = SURFACE_TILT_DEFAULT,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = SURFACE_ORIENTATION_DEFAULT,
    linke_turbidity_factor: Annotated[Optional[float], typer_option_linke_turbidity_factor] = LINKE_TURBIDITY_DEFAULT,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = ATMOSPHERIC_REFRACTION_FLAG_DEFAULT,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = REFRACTED_SOLAR_ZENITH_ANGLE_DEFAULT,
    albedo: Annotated[Optional[float], typer_option_albedo] = ALBEDO_DEFAULT,
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_declination_model: Annotated[SolarDeclinationModels, typer_option_solar_declination_model] = SolarDeclinationModels.pvlib,
    solar_position_model: Annotated[SolarPositionModels, typer_option_solar_position_model] = SolarPositionModels.noaa,
    solar_incidence_model: Annotated[SolarIncidenceModels, typer_option_solar_incidence_model] = SolarIncidenceModels.jenco,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.milne,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = TIME_OFFSET_GLOBAL_DEFAULT,
    hour_offset: Annotated[float, typer_option_hour_offset] = HOUR_OFFSET_DEFAULT,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = DAYS_IN_A_YEAR,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = PERIGEE_OFFSET,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = ECCENTRICITY_CORRECTION_FACTOR,
    time_output_units: Annotated[str, typer_option_time_output_units] = TIME_OUTPUT_UNITS_DEFAULT,
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = ANGLE_OUTPUT_UNITS_DEFAULT,
    horizon_heights: Annotated[List[float], typer_argument_horizon_heights] = None,
    system_efficiency: Annotated[Optional[float], typer_option_system_efficiency] = SYSTEM_EFFICIENCY_DEFAULT,
    efficiency_model: Annotated[PVModuleEfficiencyAlgorithms,
                                typer_option_pv_module_efficiency_algorithm] =
    PVModuleEfficiencyAlgorithms.linear,
    efficiency: Annotated[Optional[float], typer_option_efficiency] = None,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Calculate the effective hourly irradiance for a location and moment in
    time.

    The calculation applies efficiency coefficients to the direct (beam),
    diffuse, and reflected radiation considering : solar geometry,
    sun-to-surface geometry, temperature and wind speed.

    Parameters
    ----------
    use_efficiency : bool
        Flag indicating whether to consider system efficiency.
    temperature : float
        Ambient temperature in degrees Celsius.
    wind_speed : float
        Wind speed in meters per second.
    solar_constant : float
        Solar constant value.
    sun_geometry : SunGeometryVarDay
        Object containing sun geometry variables.
    surface_geometry : SunGeometryVarSlope
        Object containing sun slope geometry variables.
    solar_radiation_variables : SolarRadVar
        Object containing solar radiation variables.
    grid_geometry : GridGeometry
        Object containing grid geometry information.
    horizon_heights : ndarray
        Array of horizon elevations.
    hour_radiation_values : ndarray
        Array to store the calculated hourly radiation values.

    Returns
    -------

    Notes
    -----

    Prototype function defined in `rsun_standalone_hourly_opt.cpp`

    ``` c
    void joules_onetime(
            bool useEfficiency,
            double temperature,
            double windSpeed,
            double solar_constant,
            struct SunGeometryVarDay *sunVarGeom,
            struct SunGeometryVarSlope *sunSlopeGeom,
            struct SolarRadVar *sunRadVar,
            struct GridGeometry *gridGeom,
            double *horizonArray,
            double *hour_radiation
    )

    This function calculates the hourly radiation values (`hour_radiation`)
    for a specific moment in time,
    considering variables like
    temperature, wind speed, solar geometry, and grid geometry.

    - from: rsun_standalone_hourly_opt.cpp
    - function name: joules_onetime
    - The function calculates the hourly radiation values based on the provided inputs.
    - The calculated values are stored in the `hour_radiation_values` array.
    - The `use_efficiency` flag determines whether system efficiency is considered in the calculation.
    - Various geometric parameters and meteorological factors are used to compute the radiation values.
    Renamed variables and parameters from : to

    - useEfficiency :            use_efficiency,
    - windSpeed :                wind_speed,
    - solar_constant :           solar_constant,
    - sunVarGeom :               sun_geometry,
    - sunVarGeom.solarAltitude : sun_geometry['altitude'] to : solar_altitude
    - sunSlopeGeom :             surface_geometry,
    - sunRadVar :                solar_radiation_variables,
    - sunRadVar.cbh :            solar_radiation_variables['beam_radiation_coefficient']
    - gridGeom :                 grid_geometry,
    - horizonArray :             horizon_heights,
    - hourRadiationVals :        hour_radiation_values
    - beam_values :              beam_radiation
    - diff_values :              diffuse_radiation
    - refl_values :              reflected_radiation
    - efficiency :               efficiency
    - total_irradiance :         total_irradiance

    - bh :                       direct_radiation_coefficient

    Algorithmic structure
    
    1. If `solar_altitude` > 0 ( = sun is above the horizon) :
           proceed with checking for low sun angles

      1.1 If `solar_altitude` < 0.04 ( = very low sun angles, direct radiation is negligible) :
           `direct_horizontal_radiation` = 0

      1.2. If `solar_altitude` > 0.04 and not in_shade :
            calculate_direct_irradiance_on_tilted_surface()

    2. Calculate the diffuse and reflected irradiance

    3. Calculate the total irradiance = sum of the direct, diffuse and reflected irradiance.

    4. If apply_efficiency is True :
          calculate the efficiency coefficient as
           product of system efficiency
           and efficiency as a function of temperature and wind speed.

    5. Else, efficiency coefficient  == system efficiency

    6. Calculate the effective hourly radiation
       by applying the efficiency coefficient
       to the beam, diffuse, and reflected radiation.
    """
    in_shade = is_surface_in_shade()
    solar_declination = model_solar_declination(
        timestamp=timestamp,
        timezone=timezone,
        declination_model=solar_declination_model,
        days_in_a_year=days_in_a_year,
        eccentricity_correction_factor=eccentricity_correction_factor,
        perigee_offset=perigee_offset,
        verbose=verbose,
    )
    solar_altitude = model_solar_altitude(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_position_model=solar_position_model,
        solar_time_model=solar_time_model,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        verbose=verbose,
    )
    solar_time = model_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_time_model=solar_time_model,
        verbose=verbose,
    )
    # solar_time_decimal_hours = timestamp_to_decimal_hours(solar_time.datetime)
    # hour_angle = np.radians(15) * (solar_time.as_hours - 12)
    solar_incidence_angle = model_solar_incidence(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_time_model=solar_time_model,
        solar_incidence_model=solar_incidence_model,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        # shadow_indicator=shadow_indicator,
        # horizon_heights=horizon_heights,
        # horizon_interval=horizon_interval,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        verbose=verbose,
    )

    if solar_altitude.radians > 0.0:  # the sun is above the horizon

        if solar_altitude.radians < 0.04:  # for very low sun angles
            direct_horizontal_component = 0.0  # direct radiation is negligible
        
        # if not in_shade and solar_incidence > 0:
        elif not in_shade:  # for solar_altitude > 0.04 and a sunlit surface

            direct_irradiance = calculate_direct_inclined_irradiance_pvgis(
                longitude=longitude,
                latitude=latitude,
                elevation=elevation,
                timestamp=timestamp,
                timezone=timezone,
                direct_horizontal_component=direct_horizontal_irradiance,
                mask_and_scale=mask_and_scale,
                inexact_matches_method=inexact_matches_method,
                tolerance=tolerance,
                in_memory=in_memory,
                surface_tilt=surface_tilt,
                surface_orientation=surface_orientation,
                linke_turbidity_factor=linke_turbidity_factor,
                solar_incidence_model=solar_incidence_model,
                solar_time_model=solar_time_model,
                time_offset_global=time_offset_global,
                hour_offset=hour_offset,
                days_in_a_year=days_in_a_year,
                perigee_offset=perigee_offset,
                eccentricity_correction_factor=eccentricity_correction_factor,
                angle_output_units=angle_output_units,
                verbose=0,
            )

        # In any case
        diffuse_irradiance = calculate_diffuse_inclined_irradiance(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            timestamp=timestamp,
            timezone=timezone,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            linke_turbidity_factor=linke_turbidity_factor,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            direct_horizontal_irradiance=direct_horizontal_irradiance, # time series, optional
            apply_angular_loss_factor=apply_angular_loss_factor,
            solar_time_model=solar_time_model,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            solar_constant=solar_constant,
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
            verbose=0,
        )
        reflected_irradiance = calculate_ground_reflected_inclined_irradiance(
            longitude=longitude,
            latitude=latitude,
            elevation=elevation,
            timestamp=timestamp,
            timezone=timezone,
            surface_tilt=surface_tilt,
            surface_orientation=surface_orientation,
            linke_turbidity_factor=linke_turbidity_factor,
            apply_atmospheric_refraction=apply_atmospheric_refraction,
            albedo=albedo,
            direct_horizontal_component=direct_horizontal_irradiance, # time series, optional
            apply_angular_loss_factor=apply_angular_loss_factor,
            solar_time_model=solar_time_model,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            solar_constant=solar_constant,
            days_in_a_year=days_in_a_year,
            perigee_offset=perigee_offset,
            eccentricity_correction_factor=eccentricity_correction_factor,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
            verbose=0,
        )

    else:  # the sun is below the horizon
        direct_irradiance = diffuse_irradiance = reflected_irradiance = 0

    if not efficiency_model and not efficiency:
        efficiency_coefficient = system_efficiency

    if not efficiency_model and efficiency:
        efficiency_coefficient = efficiency

    if efficiency_model and not efficiency:
        total_irradiance = direct_irradiance + diffuse_irradiance + reflected_irradiance
        # total_irradiance = np.sum(direct_radiation) + np.sum(diffuse_radiation) + np.sum(reflected_radiation)
        efficiency_coefficient = calculate_pv_efficiency(
            irradiance=total_irradiance,
            temperature=temperature,
            model_constants=EFFICIENCY_MODEL_COEFFICIENTS_DEFAULT,
            standard_test_temperature=TEMPERATURE_DEFAULT,
            wind_speed=wind_speed,
            use_faiman_model=False,
        )

    result = efficiency_coefficient * np.array([direct_irradiance, diffuse_irradiance, reflected_irradiance])

    if verbose == 3:
        debug(locals())
    if verbose > 1:
        print(f'Direct, Diffuse, Reflected : {direct_irradiance}, {diffuse_irradiance}, {reflected_irradiance} * {efficiency_coefficient} efficiency factor')
        print(f'Effective irradiance values : {result}')
    if verbose > 0:
        print(f'Total irradiance : {np.sum(result)}')
    return result
