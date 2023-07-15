from math import cos
from typing import Annotated
from typing import List
from typing import Optional
import math
import numpy as np
import typer


def calculate_hourly_radiation(
        use_efficiency: bool,
        temperature: float,
        wind_speed: float,
        solar_constant: float,
        sun_geometry,
        sun_surface_geometry,
        solar_radiation_variables,
        grid_geometry,
        horizon_heights,
        hour_radiation_values
    ):
    """Calculate hourly radiation values for a specific moment in time.
    
    Calculate hourly radiation values for a specific moment in time considering
    variables like temperature, wind speed, solar geometry, and grid geometry.

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
    """
    direct_radiation_coefficient = 0  # NEEDED?
    total_irradiance = 0.0
    efficiency = 0.0

    direct_radiation = np.zeros(3)  # beam_radiation = np.zeros(3)
    diffuse_radiation = np.zeros(3)
    reflected_radiation = np.zeros(3)

    is_shadow = sun_geometry['is_shadow']
    
    if solar_altitude > 0:

        if solar_altitude < 0.04:
            # At very low solar altitude ignore direct (beam) radiation
            direct_horizontal_radiation_coefficient = 0
        
        if not is_shadow and solar_altitude > 0:
            calculate_direct_radiation_for_tilted_surface(
                    direct_horizontal_radiation_coefficient,  # bh : is it the coefficient or the direct radiation required here?
                    solar_altitude,
                    incidence_angle,
                    )

        else:
            direct_horizontal_radiation_coefficient = 0
        
        drad_angle_irradiance(
                solar_constant,
                bh,
                sun_geometry,
                sunSlopeGeom,
                solar_radiation_variables,
                diffuse_radiation,
                reflected_radiation
                )
    
    total_irradiance = np.sum(beam_radiation) + np.sum(diffuse_radiation) + np.sum(reflected_radiation)
    
    if useEfficiency:
        efficiency = systemEfficiency() * efficiency_ww(total_irradiance, temperature, windSpeed)

    else:
        efficiency = systemEfficiency()
    
    efficiency = max(effic, 0.0)
    
    hour_radiation[0] = efficiency * beam_radiation[0]
    hour_radiation[1] = efficiency * diffuse_radiation[0]
    hour_radiation[2] = efficiency * reflected_radiation[0]
    hour_radiation[3:6] = beam_radiation[0], diffuse_radiation[0], reflected_radiation[0]
    hour_radiation[6:9] = beam_radiation[1], diffuse_radiation[1], reflected_radiation[1]

    pass
