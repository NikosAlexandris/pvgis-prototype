from math import cos
from typing import Annotated
from typing import List
from typing import Optional
import math
import numpy as np
import typer


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
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f"Estimate the direct solar radiation",
)


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


def calculate_diffuse_irradiance(
    solar_constant,
    bh,
    sun_geometry,
    sunSlopeGeom,
    solar_radiation_variables,
    diffuse_radiation,
    reflected_radiation,
):
    # Placeholder for drad_angle_irradiance
    pass


def calculate_reflected_irradiance(
    solar_constant,
    bh,
    sun_geometry,
    sunSlopeGeom,
    solar_radiation_variables,
    diffuse_radiation,
    reflected_radiation,
):
    # Placeholder for drad_angle_irradiance
    pass



# @numba.jit(nopython=True)
@app.callback('effective', no_args_is_help=True)
def calculate_effective_irradiance(
        longitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-180, max=180)],
        latitude: Annotated[float, typer.Argument(
            callback=convert_to_radians,
            min=-90, max=90)],
        elevation: Annotated[float, typer.Argument(
            min=0, max=8848)],
        solar_constant: Annotated[float, typer.Argument(help="Solar constant value.")],
        temperature: Annotated[float, typer.Argument(help="Ambient temperature in degrees Celsius.")],
        wind_speed: Annotated[float, typer.Argument(help="Wind speed in meters per second.")],
        timestamp: Annotated[Optional[datetime], typer.Argument(
            help='Timestamp',
            default_factory=now_utc_datetimezone)],
        timezone: Annotated[Optional[str], typer.Option(
            help='Timezone',
            callback=ctx_convert_to_timezone)] = None,
        surface_tilt: Annotated[Optional[float], typer.Argument(
            min=0, max=90)] = 0,
        surface_orientation: Annotated[Optional[float], typer.Argument(
            min=0, max=360)] = 180,
        linke_turbidity_factor: Annotated[float, typer.Argument(
            help='A measure of atmospheric turbidity, equal to the ratio of total optical depth to the Rayleigh optical depth',
            min=0, max=10)] = 2,  # 2 to get going for now
        solar_incidence_angle_model: Annotated[SolarIncidenceAngleMethod, typer.Option(
            '--incidence-angle-model',
            show_default=True,
            show_choices=True,
            case_sensitive=False,
            help="Method to calculate the solar declination")] = 'jenco',
        solar_time_model: Annotated[SolarTimeModels, typer.Option(
            '--solar-time-model',
            help="Model to calculate solar position",
            show_default=True,
            show_choices=True,
            case_sensitive=False)] = SolarTimeModels.skyfield,
        days_in_a_year: Annotated[float, typer.Option(
            help='Days in a year')] = 365.25,
        perigee_offset: Annotated[float, typer.Option(
            help='Perigee offset')] = 0.048869,
        orbital_eccentricity: Annotated[float, typer.Option(
            help='Eccentricity')] = 0.01672,
        time_offset_global: Annotated[float, typer.Option(
            help='Global time offset')] = 0,
        hour_offset: Annotated[float, typer.Option(
            help='Hour offset')] = 0,
        angle_output_units: Annotated[str, typer.Option(
            '-u',
            '--units',
            show_default=True,
            case_sensitive=False,
            help="Angular units for the calculated solar azimuth output (degrees or radians)")] = 'radians',
        horizon_heights: Annotated[List[float], typer.Argument(help="Array of horizon elevations.")] = None,
        system_efficiency: Optional[float] = 0.86,
        efficiency = None,
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
            output_units=output_units
        )
    )
    incidence_angle = calculate_solar_incidence_angle()

    # direct_horizontal_radiation = get_direct_horizontal_radiation()
    direct_horizontal_radiation = calculate_direct_horizontal_radiation()
    
    if solar_altitude > 0.0:  # the sun is above the horizon

        if solar_altitude < 0.04:  # for very low sun angles
            direct_horizontal_radiation = 0.0  # direct radiation is negligible
        
        # if not in_shade and solar_incidence > 0:
        elif not in_shade:  # for solar_altitude > 0.04 and a sunlit surface
            direct_horizontal_radiation = calculate_direct_irradiatiance_on_tilted_surface(
                    direct_horizontal_radiation,
                    solar_altitude,
                    incidence_angle,
                )

        # In any case
        diffuse_irradiance = calculate_diffuse_irradiance_on_tilted_surface(
            solar_constant,
            direct_horizontal_radiation,
            sun_geometry,
            sun_surface_geometry,
            solar_radiation_variables,
            diffuse_radiation,
            reflected_radiation,
        )
        reflected_irradiance = calculate_reflected_irradiance_on_tilted_surface(
            solar_constant,
            direct_horizontal_radiation,
            sun_geometry,
            sun_surface_geometry,
            solar_radiation_variables,
            diffuse_radiation,
            reflected_radiation,
        )

    else:  # the sun is below the horizon
        direct_irradiance = diffuse_irradiance = reflected_irradiance = 0

    total_irradiance = direct_horizontal_radiation + diffuse_horizontal_radiation + reflected_horizontal_radiation
    # total_irradiance = np.sum(direct_radiation) + np.sum(diffuse_radiation) + np.sum(reflected_radiation)
    
    if apply_efficiency:
        efficiency_coefficient = system_efficiency * efficiency_ww(
            total_irradiance, temperature, wind_speed
        )
    else:
        efficiency_coefficient = system_efficiency
    
    # ?
    efficiency_coefficient = max(efficiency_coefficient, 0.0)  # limit to zero
    
    return efficiency_coefficient * np.array([direct_horizontal_radiation, diffuse_horizontal_radiation, reflected_horizontal_radiation])
