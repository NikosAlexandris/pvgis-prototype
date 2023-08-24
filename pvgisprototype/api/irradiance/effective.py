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
from pvgisprototype.api.geometry.solar_altitude import calculate_solar_altitude
from pvgisprototype.api.input_models import SolarAltitudeInput
from pvgisprototype.api.geometry.time_models import SolarTimeModels
from ..utilities.conversions import convert_to_radians
from ..utilities.timestamp import now_utc_datetimezone
from ..utilities.timestamp import ctx_convert_to_timezone
from pvgisprototype.api.irradiance.direct import SolarIncidenceAngleMethod
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
from pvgisprototype.models.standard.solar_incidence import calculate_solar_incidence
from ..geometry.solar_declination import calculate_solar_declination
from ..geometry.solar_time import model_solar_time
from ..utilities.timestamp import timestamp_to_decimal_hours
from .direct import calculate_direct_horizontal_irradiance

from pvgisprototype.cli.typer_parameters import OrderCommands
from pvgisprototype.cli.typer_parameters import typer_option_refracted_solar_zenith

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
    longitude: Annotated[float, typer.Argument(
        callback=convert_to_radians,
        min=-180, max=180)],
    latitude: Annotated[float, typer.Argument(
        callback=convert_to_radians,
        min=-90, max=90)],
    elevation: Annotated[float, typer.Argument(
        min=0, max=8848,
        help='Elevation',)],
    timestamp: Annotated[Optional[datetime], typer.Argument(
        help='Timestamp',
        default_factory=now_utc_datetimezone)],
    direct_horizontal_irradiance: Annotated[Path, typer.Option(
        help='Path to direct horizontal irradiance time series (Surface Incoming Direct radiation (SID), `fdir`)',
        rich_help_panel=rich_help_panel_series_irradiance,
        )] = None,
    temperature: Annotated[float, typer.Argument(
        help="Ambient temperature in degrees Celsius.")] = 25,
    wind_speed: Annotated[float, typer.Argument(
        help="Wind speed in meters per second.")] = 0,
    mask_and_scale: Annotated[bool, typer.Option(
        help="Mask and scale the series",
        rich_help_panel=rich_help_panel_series_irradiance,
        )] = False,
    inexact_matches_method: Annotated[MethodsForInexactMatches, typer.Option(
        '--method-for-inexact-matches',
        show_default=True,
        show_choices=True,
        case_sensitive=False,
        rich_help_panel=rich_help_panel_series_irradiance,
        help="Model to calculate solar position")] = MethodsForInexactMatches.nearest,
    tolerance: Annotated[float, typer.Option(
        # help=f'Maximum distance between original and new labels for inexact matches. See nearest-neighbor-lookups Xarray documentation',
        help=f'Maximum distance between original and new labels for inexact matches. See [nearest-neighbor-lookups](https://docs.xarray.dev/en/stable/user-guide/indexing.html#nearest-neighbor-lookups) @ Xarray documentation',
        rich_help_panel=rich_help_panel_series_irradiance,
        )] = 0.1,
    in_memory: Annotated[bool, typer.Option(
        help='Load data into memory',
        rich_help_panel=rich_help_panel_series_irradiance,
        )] = False,
    timezone: Annotated[Optional[str], typer.Option(
        help='Timezone',
        callback=ctx_convert_to_timezone)] = None,
    surface_tilt: Annotated[Optional[float], typer.Option(
        min=0, max=90,
        help='Solar surface tilt angle',
        callback=convert_to_radians,
        rich_help_panel=rich_help_panel_geometry_surface)] = 45,
    surface_orientation: Annotated[Optional[float], typer.Option(
        min=0, max=360,
        help='Solar surface orientation angle. [yellow]Due north is 0 degrees.[/yellow]',
        callback=convert_to_radians,
        rich_help_panel=rich_help_panel_geometry_surface)] = 180,  # from North!
    linke_turbidity_factor: Annotated[float, typer.Option(
        help='Ratio of total to Rayleigh optical depth measuring atmospheric turbidity',
        min=0, max=8,
        rich_help_panel=rich_help_panel_atmospheric_properties,
        )] = 2,  # 2 to get going for now
    apply_atmospheric_refraction: Annotated[Optional[bool], typer.Option(
        '--atmospheric-refraction',
        help='Apply atmospheric refraction functions',
        rich_help_panel=rich_help_panel_advanced_options,
        )] = True,
    refracted_solar_zenith: Annotated[Optional[float], typer_option_refracted_solar_zenith] = 1.5853349194640094,  # radians
    albedo: Annotated[Optional[float], typer.Option(
        min=0,
        help='Mean ground albedo',
        rich_help_panel=rich_help_panel_advanced_options)] = 2,
    apply_angular_loss_factor: Annotated[Optional[bool], typer.Option(
        help='Apply angular loss function',
        rich_help_panel=rich_help_panel_advanced_options)] = True,
    solar_incidence_angle_model: Annotated[SolarIncidenceAngleMethod, typer.Option(
        '--incidence-angle-model',
        show_default=True,
        show_choices=True,
        case_sensitive=False,
        help="Method to calculate the solar declination")] = 'jenco',
    solar_time_model: Annotated[SolarTimeModels, typer.Option(
        help="Model to calculate solar position",
        show_default=True,
        show_choices=True,
        case_sensitive=False,
        rich_help_panel=rich_help_panel_solar_time)] = SolarTimeModels.skyfield,
    time_offset_global: Annotated[float, typer.Option(
        help='Global time offset',
        rich_help_panel=rich_help_panel_solar_time)] = 0,
    hour_offset: Annotated[float, typer.Option(
        help='Hour offset',
        rich_help_panel=rich_help_panel_solar_time)] = 0,
    solar_constant: Annotated[float, typer.Option(
        help="The mean solar electromagnetic radiation at the top of the atmosphere (~1360.8 W/m2) one astronomical unit (au) away from the Sun.",
        min=1360,
        rich_help_panel=rich_help_panel_earth_orbit)] = SOLAR_CONSTANT,
    days_in_a_year: Annotated[float, typer.Option(
        help='Days in a year',
        rich_help_panel=rich_help_panel_earth_orbit)] = 365.25,
    perigee_offset: Annotated[float, typer.Option(
        help='Perigee offset',
        rich_help_panel=rich_help_panel_earth_orbit)] = 0.048869,
    eccentricity: Annotated[float, typer.Option(
        help='Eccentricity',
        rich_help_panel=rich_help_panel_earth_orbit)] = 0.01672,
    time_output_units: Annotated[str, typer.Option(
        show_default=True,
        case_sensitive=False,
        help="Time units for output and internal calculations (seconds, minutes or hours) - :warning: [bold red]Keep fingers away![/bold red]",
        rich_help_panel=rich_help_panel_output)] = 'minutes',
    angle_units: Annotated[str, typer.Option(
        show_default=True,
        case_sensitive=False,
        help="Angular units for internal solar geometry calculations. :warning: [bold red]Keep fingers away![/bold red]",
        rich_help_panel=rich_help_panel_output,
        )] = 'radians',
    angle_output_units: Annotated[str, typer.Option(
        show_default=True,
        case_sensitive=False,
        help="Angular units for solar geometry calculations (degrees or radians). :warning: [bold red]Under development[/red bold]",
        rich_help_panel=rich_help_panel_output,
        )] = 'radians',
    horizon_heights: Annotated[List[float], typer.Argument(help="Array of horizon elevations.")] = None,
    system_efficiency: Optional[float] = 0.86,
    efficiency: Annotated[Optional[float], typer.Option(
        '-e',
        help='Apply efficieny',
        rich_help_panel=rich_help_panel_efficiency,
        )] = None,
    verbose: Annotated[bool, typer.Option(
        help='Be verbose!')] = False,
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
    solar_altitude = calculate_solar_altitude(
        longitude=longitude,
        latitude=latitude,
        timestamp=timestamp,
        timezone=timezone,
        apply_atmospheric_refraction=apply_atmospheric_refraction,
        refracted_solar_zenith=refracted_solar_zenith,
        days_in_a_year=days_in_a_year,
        perigee_offset=perigee_offset,
        eccentricity=eccentricity,
        time_offset_global=time_offset_global,
        hour_offset=hour_offset,
        solar_time_model=solar_time_model,
        time_output_units=time_output_units,
        angle_units=angle_units,
        angle_output_units=angle_output_units,
        )
    solar_declination = calculate_solar_declination(
            timestamp=timestamp,
            timezone=timezone,
            days_in_a_year=days_in_a_year,
            orbital_eccentricity=eccentricity,
            perigee_offset=perigee_offset,
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
            eccentricity=eccentricity,
            time_offset_global=time_offset_global,
            hour_offset=hour_offset,
            time_output_units=time_output_units,
            angle_units=angle_units,
            angle_output_units=angle_output_units,
    )
    solar_time_decimal_hours = timestamp_to_decimal_hours(solar_time)
    hour_angle = np.radians(15) * (solar_time_decimal_hours - 12)
    solar_incidence_angle = calculate_solar_incidence(
        latitude,
        solar_declination,
        surface_tilt,
        surface_orientation,
        hour_angle,
        output_units=angle_output_units,
        )

    if solar_altitude > 0.0:  # the sun is above the horizon

        if solar_altitude < 0.04:  # for very low sun angles
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
                solar_incidence_angle_model=solar_incidence_angle_model,
                solar_time_model=solar_time_model,
                time_offset_global=time_offset_global,
                hour_offset=hour_offset,
                days_in_a_year=days_in_a_year,
                perigee_offset=perigee_offset,
                eccentricity=eccentricity,
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
            eccentricity=eccentricity,
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
            eccentricity=eccentricity,
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
    
    return efficiency_coefficient * np.array([direct_irradiance, diffuse_irradiance, reflected_irradiance])
