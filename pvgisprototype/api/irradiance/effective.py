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


from pvgisprototype.api.irradiance.direct import calculate_direct_inclined_irradiance_pvgis
# from pvgisprototype.api.irradiance.diffuse import calculate_diffuse_inclined_irradiance
# from pvgisprototype.api.irradiance.reflected import calculate_reflected_inclined_irradiance_pvgis

from datetime import datetime
from pvgisprototype.api.function_models import ModelSolarPositionInputModel
from pvgisprototype.api.geometry.models import SolarDeclinationModels
from pvgisprototype.api.geometry.models import SolarPositionModels
from pvgisprototype.api.geometry.models import SolarTimeModels
from ..utilities.conversions import convert_to_radians
from ..utilities.timestamp import now_utc_datetimezone
from ..utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.api.irradiance.direct import SolarIncidenceModels
from .constants import SOLAR_CONSTANT
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_series_irradiance
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_toolbox
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_advanced_options
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_geometry_surface
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_solar_time
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_efficiency
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_atmospheric_properties
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_earth_orbit
from pvgisprototype.cli.rich_help_panel_names import rich_help_panel_output

from pvgisprototype.api.irradiance.diffuse import  calculate_diffuse_inclined_irradiance
from pvgisprototype.api.irradiance.reflected import  calculate_ground_reflected_inclined_irradiance
from pvgisprototype.api.geometry.solar_incidence import model_solar_incidence
from pvgisprototype.api.geometry.solar_declination import model_solar_declination
from pvgisprototype.api.geometry.solar_altitude import model_solar_altitude
from ..geometry.solar_time import model_solar_time
from ..utilities.timestamp import timestamp_to_decimal_hours
from .direct import calculate_direct_horizontal_irradiance

from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_argument_longitude
from pvgisprototype.cli.typer_parameters import typer_argument_latitude
from pvgisprototype.cli.typer_parameters import typer_argument_elevation
from pvgisprototype.cli.typer_parameters import typer_argument_timestamp
from pvgisprototype.cli.typer_parameters import typer_option_start_time
from pvgisprototype.cli.typer_parameters import typer_option_end_time
from pvgisprototype.cli.typer_parameters import typer_option_timezone
from pvgisprototype.cli.typer_parameters import typer_argument_direct_horizontal_irradiance
from pvgisprototype.cli.typer_parameters import typer_argument_temperature_time_series
from pvgisprototype.cli.typer_parameters import typer_argument_wind_speed_time_series
from pvgisprototype.cli.typer_parameters import typer_option_mask_and_scale
from pvgisprototype.cli.typer_parameters import typer_option_inexact_matches_method
from pvgisprototype.cli.typer_parameters import typer_option_tolerance
from pvgisprototype.cli.typer_parameters import typer_option_in_memory
from pvgisprototype.cli.typer_parameters import typer_argument_surface_tilt
from pvgisprototype.cli.typer_parameters import typer_argument_surface_orientation
from pvgisprototype.cli.typer_parameters import typer_option_linke_turbidity_factor
from pvgisprototype.cli.typer_parameters import typer_option_apply_atmospheric_refraction
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith
from pvgisprototype.cli.typer_parameters import typer_option_albedo
from pvgisprototype.cli.typer_parameters import typer_option_apply_angular_loss_factor
from pvgisprototype.cli.typer_parameters import typer_option_solar_incidence_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_declination_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_position_model
from pvgisprototype.cli.typer_parameters import typer_option_solar_time_model
from pvgisprototype.cli.typer_parameters import typer_option_global_time_offset
from pvgisprototype.cli.typer_parameters import typer_option_hour_offset
from pvgisprototype.cli.typer_parameters import typer_option_solar_constant
from pvgisprototype.cli.typer_parameters import typer_option_days_in_a_year
from pvgisprototype.cli.typer_parameters import typer_option_perigee_offset
from pvgisprototype.cli.typer_parameters import typer_option_eccentricity_correction_factor
from pvgisprototype.cli.typer_parameters import typer_option_time_output_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_units
from pvgisprototype.cli.typer_parameters import typer_option_angle_output_units
from pvgisprototype.cli.typer_parameters import typer_option_efficiency
from pvgisprototype.cli.typer_parameters import typer_option_rounding_places
from pvgisprototype.cli.typer_parameters import typer_option_verbose

model_constants=[]
model_constants.append(94.804)
model_constants.append(3.151)
model_constants.append(-0.8768)
model_constants.append(-0.32148)
model_constants.append(0.003795)
model_constants.append(-0.001056)
model_constants.append(-0.0005247)
model_constants.append(0.035)

AOIConstants = []
AOIConstants.append(-0.074)
AOIConstants.append(0.155)


app = typer.Typer(
    cls=OrderCommands,
    add_completion=False,
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


def system_efficiency():
    return 0.86


# @app.command('efficiency')
def calculate_efficiency(
    irradiance,
    model_constants,
    system_efficiency,
    temperature,
    wind_speed,
    cell_temperature_under_standard_test_conditions: float = 25,  # degrees Celsius.
):
    """
    # Calculate the efficiency coefficient as
    # product of system efficiency
    # and efficiency as a function of total irradiance, temperature, and wind speed.
    """
    relative_irradiance = 0.001 * irradiance  # what is this exactly?
    if relative_irradiance <= 0:
        return 0

    ln_relative_irradiance = np.log(relative_irradiance)
    temperature = irradiance / (model_constants[7] + model_constants[8] * windspeed) + temperature
    temperature_deviation_from_standard = temperature - cell_temperature_under_standard_test_conditions
    pm = (
        model_constants[0]
        + ln_relative_irradiance
        * (model_constants[1] + ln_relative_irradiance * model_constants[2])
        + temperature_deviation_from_standard
        * (
            model_constants[3]
            + ln_relative_irradiance
            * (model_constants[4] + ln_relative_irradiance * model_constants[5])
            + model_constants[6] * temperature_deviation_from_standard
        )
    )
    efficiency = pm / model_constants[0]

    # Check the output before returning
    if not np.isfinite(efficiency):
        raise ValueError("The computed efficiency is not a finite number.")
    elif not 0 <= efficiency <= 1:
        raise ValueError("The computed efficiency is not within the expected range (0 to 1).")

    return pm / model_constants[0]


# @numba.jit(nopython=True)
@app.callback(
        'effective',
       invoke_without_command=True,
       no_args_is_help=True,
       # context_settings={"ignore_unknown_options": True},
       help=f'Calculate the clear-sky ground reflected irradiance',
       )
def calculate_effective_irradiance(
    longitude: Annotated[float, typer_argument_longitude],
    latitude: Annotated[float, typer_argument_latitude],
    elevation: Annotated[float, typer_argument_elevation],
    timestamp: Annotated[Optional[datetime], typer_argument_timestamp],
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    timezone: Annotated[Optional[str], typer_option_timezone] = None,
    direct_horizontal_irradiance: Annotated[Optional[Path], typer_argument_direct_horizontal_irradiance] = None,
    temperature: Annotated[float, typer_argument_temperature_time_series] = 25,
    wind_speed: Annotated[float, typer_argument_wind_speed_time_series] = 0,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer_option_inexact_matches_method] = MethodsForInexactMatches.nearest,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    surface_tilt: Annotated[Optional[float], typer_argument_surface_tilt] = 45,
    surface_orientation: Annotated[Optional[float], typer_argument_surface_orientation] = 180,
    linke_turbidity_factor: Annotated[Optional[float], typer_option_linke_turbidity_factor] = 2,
    apply_atmospheric_refraction: Annotated[Optional[bool], typer_option_apply_atmospheric_refraction] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = 1.5853349194640094,  # radians
    albedo: Annotated[Optional[float], typer_option_albedo] = 2,
    apply_angular_loss_factor: Annotated[Optional[bool], typer_option_apply_angular_loss_factor] = True,
    solar_declination_model: Annotated[SolarDeclinationModels, typer_option_solar_declination_model] = SolarDeclinationModels.pvis,
    solar_position_model: Annotated[SolarPositionModels, typer_option_solar_position_model] = SolarPositionModels.skyfield,
    solar_incidence_model: Annotated[SolarIncidenceModels, typer_option_solar_incidence_model] = SolarIncidenceModels.jenco,
    solar_time_model: Annotated[SolarTimeModels, typer_option_solar_time_model] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer_option_global_time_offset] = 0,
    hour_offset: Annotated[float, typer_option_hour_offset] = 0,
    solar_constant: Annotated[float, typer_option_solar_constant] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer_option_days_in_a_year] = 365.25,
    perigee_offset: Annotated[float, typer_option_perigee_offset] = 0.048869,
    eccentricity_correction_factor: Annotated[float, typer_option_eccentricity_correction_factor] = 0.03344,
    time_output_units: Annotated[str, typer_option_time_output_units] = 'minutes',
    angle_units: Annotated[str, typer_option_angle_units] = 'radians',
    angle_output_units: Annotated[str, typer_option_angle_output_units] = 'radians',
    horizon_heights: Annotated[List[float], typer.Argument(help="Array of horizon elevations.")] = None,
    system_efficiency: Optional[float] = 0.86,
    efficiency: Annotated[Optional[float], typer_option_efficiency] = None,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = 5,
    verbose: Annotated[bool, typer_option_verbose] = False,
    ):
    """Calculate hourly radiation values for a specific moment in time.
    
    Calculate hourly radiation values for a specific moment in time considering
    :
    - solar geometry
    - the sun-to-surface geometry
    - temperature
    - wind speed

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
    None
    """
    """
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
        model=solar_declination_model,
        days_in_a_year=days_in_a_year,
        eccentricity_correction_factor=eccentricity_correction_factor,
        perigee_offset=perigee_offset,
        angle_output_units=angle_output_units,
    )
    solar_altitude = model_solar_altitude(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_time_model=solar_time_model,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    solar_time = model_solar_time(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        model=solar_time_model,
        refracted_solar_zenith=refracted_solar_zenith,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
    )
    solar_time_decimal_hours = timestamp_to_decimal_hours(solar_time)
    hour_angle = np.radians(15) * (solar_time_decimal_hours - 12)
    solar_incidence_angle = model_solar_incidence(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        solar_time_model=solar_time_model,
        solar_incidence_model=solar_incidence_model,
        hour_angle=hour_angle,
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        # shadow_indicator=shadow_indicator,
        # horizon_heights=horizon_heights,
        # horizon_interval=horizon_interval,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity_correction_factor=eccentricity_correction_factor,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        verbose=verbose,
    )

    if solar_altitude.value > 0.0:  # the sun is above the horizon

        if solar_altitude.value < 0.04:  # for very low sun angles
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
                verbose=verbose,
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
        )

    else:  # the sun is below the horizon
        direct_irradiance = diffuse_irradiance = reflected_irradiance = 0

    if not efficiency:
        efficiency_coefficient = system_efficiency

    else:
        total_irradiance = direct_irradiance + diffuse_irradiance + reflected_irradiance
        # total_irradiance = np.sum(direct_radiation) + np.sum(diffuse_radiation) + np.sum(reflected_radiation)
        efficiency_coefficient = system_efficiency * efficiency_ww(
            total_irradiance, temperature, wind_speed
        )

    # ?
    efficiency_coefficient = max(efficiency_coefficient, 0.0)  # limit to zero
    
    result = efficiency_coefficient * np.array([direct_irradiance, diffuse_irradiance, reflected_irradiance])
    debug(locals())
    return result
