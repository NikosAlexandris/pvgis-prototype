"""
This module defines Pydantic models for representing solar data attributes over
a specific location.

Models
------
- Location:                 Geographical coordinates of a location.
- LocationSolarAttributes:  Various variables associated with a location.
- SolarGeometryConstants:     Constant sun geometry data for a day.
- SolarGeometryVariables:     The variable sun geometry data for a day.
- SunSurfaceGeometry:       The sun-surface geometry data
- SolarRadiationVariables: 
- GridGeometry

In the original C/C++ source code of PVGIS, the corresponding `struct`s for data, are:

- Location                <- PointData: struct
- LocationSolarAttributes <- PointVarData: struct
- SolarGeometryConstants    <- SolarGeometryConstDay : struct
- SolarGeometryVariables    <- SolarGeometryVarDay : struct
- SunSurfaceGeometry      <- SolarGeometryVarSlope : struct
- SolarRadiationVariables <- SolarRadVar : struct
- GridGeometry            <- GridGeometry : struct

Usage
-----
Import the models from this module into your code and use them to validate and manipulate solar data.

Example
-------
from models import Location, LocationSolarAttributes

# Create an instance of Location
location = Location(latitude=37.7749, longitude=-122.4194, elevation=10.0)

# Validate and access the data

if location.validate():
    print(location.latitude)
    print(location.longitude)
    print(location.elevation)

# Create an instance of LocationSolarAttributes

location_solar_attributes = LocationSolarAttributes(
    linkeTurbidity=2.0,
    beamCoefficient=0.8,
    diffCoefficient=0.5,
    declination=23.5,
    temperatureCoeffs=[0.1, 0.2, 0.3],
    # ... rest of the attributes
)

# Validate and access the data

if location_solar_attributes.validate():
    print(location_solar_attributes.linkeTurbidity)
    print(location_solar_attributes.beamCoefficient)
    print(location_solar_attributes.diffCoefficient)
    # ... rest of the attributes
"""

from pydantic import BaseModel
from pydantic import Field
from typing import List
from typing import Optional
from math import degrees
from math import radians
from math import cos
from math import sin
from math import pi
from math import acos
from math import fabs
import numpy as np
import logging


class Location(BaseModel):
    """
    Represents the geographical coordinates of a location.

    Attributes:
    - elevation (float): The elevation of the location.
    - latitude (float): The latitude of the location.
    - longitude (float): The longitude of the location.

    Usage:
    Create an instance of PointData to represent a specific geographical location.

    Example:
    location = PointData(elevation=10.0, latitude=37.7749, longitude=-122.4194)
    """

    elevation: float
    latitude: float
    longitude: float


class LocationSolarAttributes(BaseModel):
    """
    Represents solar attributes and variables for a specific location.

    Attributes:
    - linke_turbidity (float): The Linke turbidity coefficient.
    - direct_radiation_coefficient (float): The direct (or beam) radiation coefficient.
    - diffuse_radiation_coefficient (float): The diffuse radiation coefficient.
    - declination (float): The solar declination angle.
    - temperature_coeffs (List[float]): The coefficients for temperature calculations.
    - temp_std (float): The standard deviation of temperature.
    - rad_std (float): The standard deviation of radiation.
    - pdf_data (List[float]): The PDF data.
    - min_temp (float): The minimum temperature.
    - max_temp (float): The maximum temperature.
    - wind_speed (float): The wind speed.
    - wind_direction (float): The wind direction.
    - dewpoint_temperature (float): The dew point temperature.
    - rel_humidity (float): The relative humidity.
    - pressure (float): The atmospheric pressure.
    - strd (float): The solar time resolution divisor.
    - day (int): The day of the month.

    Usage:
    Create an instance of LocationSolarAttributes to represent solar attributes and variables for a specific location.

    Example:
    location_attributes = LocationSolarAttributes(
        linke_turbidity=2.0,
        direct_radiation_cefficient=0.8,
        diffuse_radiation_coefficient=0.2,
        declination=23.5,
        temperature_coeffs=[0.5, 0.2, -0.1],
        temp_std=1.0,
        rad_std=0.5,
        pdf_data=[0.1, 0.2, 0.3],
        min_temp=-10.0,
        max_temp=30.0,
        wind_speed=10.0,
        wind_direction=180.0,
        dewpoint_temperature=5.0,
        rel_humidity=0.6,
        pressure=1013.25,
        strd=4.0,
        day=15
    )
    """

    linke_turbidity: float
    direct_radiation_coefficient: float
    diffuse_radiation_coefficient: float
    declination: float
    temperature_coeffs: List[float]
    temp_std: float
    rad_std: float
    pdf_data: List[float]
    min_temp: float
    max_temp: float
    wind_speed: float
    wind_direction: float
    dewpoint_temperature: float
    rel_humidity: float
    pressure: float
    strd: float
    day: int


class GridGeometry(BaseModel):
    sine_latitude: float
    cosine_latitude: float


class SolarGeometryDayConstants(BaseModel):
    """
    Represents the constant sun geometry data for a day.

    Notes
    -----

    lum_C?? : Are these (in the original code) indeed luminance?
    local_solar_time: `longitTime` set to 0 in the original source code!
    """

    longitude: float = Field(..., description="The longitude of the location.")
    latitude: float = Field(..., description="The latitude of the location.")
    # local_solar_time: float = Field(0, description="The local solar time.")
    solar_declination: float = Field(..., description="The solar declination.")
    # time_offset: float = Field(0, description="The time offset.")
    cosine_solar_declination: float = Field(
        None, description="The cosine of the solar declination."
    )
    sine_solar_declination: float = Field(
        None, description="The sine of the solar declination."
    )
    lum_C11: float = Field(None, description="The value of luminance C11.")
    lum_C13: float = Field(None, description="The value of luminance C13.")
    lum_C22: float = Field(None, description="The value of luminance C22.")
    lum_C31: float = Field(None, description="The value of luminance C31.")
    lum_C33: float = Field(None, description="The value of luminance C33.")
    sunrise_time: float = Field(None, description="The time of sunrise.")
    sunset_time: float = Field(None, description="The time of sunset.")

    def __str__(self):
        attributes = "\n".join(
            f"{key.replace('_', ' ').capitalize()}: {value}"
            for key, value in self.dict().items()
        )
        return f"Solar Geometry Day Constants\n{attributes}"


class SolarGeometryDayVariables(BaseModel):
    """
    Represents the variable sun geometry data for a day.
    """

    is_shadow: bool = Field(False, description="Indicates whether there is a shadow.")
    # z_orig: float = Field(..., description="The original Z value.")
    # z_max: float = Field(..., description="The maximum Z value.")
    # zp: float = Field(..., description="The Zp value.")
    solar_altitude: float = Field(..., description="The solar altitude.")
    sine_solar_altitude: float = Field(..., description="The sine of solar altitude.")
    tan_solar_altitude: float = Field(..., description="The tangent of solar altitude.")
    solar_azimuth: float = Field(..., description="The solar azimuth.")
    sun_azimuth_angle: float = Field(..., description="The sun azimuth angle.")
    # step_sine_angle: float
    # step_cosine_angle: float

    def __str__(self):
        attributes = "\n".join(
            f"{key.replace('_', ' ').capitalize()}: {value}"
            for key, value in self.dict().items()
        )
        return f"Solar Geometry Day Variables\n{attributes}"


class SunSurfaceGeometry(BaseModel):
    """
    Represents the variable sun-to-surface geometry.
    The terminology aims to be compatible with pvlib!

    Attributes:
    - longitude_difference: The longitude difference.
    - luminance_C31_long: The luminance C31 for the longitude.
    - luminance_C33_long: The luminance C33 for the longitude.
    - tilt: The tilt angle of the surface.
    - azimuth : The azimuth angle of the surface.
    - sin_tilt: The sine of the surface tilt.
    - cos_tilt: The cosine of the surface tilt.

    Notes
    -----

    In rsun, the corresponding terms are:

    - tilt : slope
    - azimuth : aspect or orientation
    """

    longitude_difference: float
    luminance_C31_long: float
    luminance_C33_long: float
    slope: float
    aspect: float
    sin_slope: float
    cos_slope: float


class SolarRadiationVariables(BaseModel):
    """
    Represents the solar radiation variables.

    Attributes:
    - direct_radiation_cefficient: The direct (or beam) radiation coefficient.
    - diffuse_radiation_coefficient: The diffuse radiation coefficient.
    - linke_turbidity: The Linke turbidity.
    - extraterrestrial_direct_normal_irradiance : The direct normal irradiance
      at the top of the atmosphere (extraterrestrial)
    - albedo: The albedo.

    Notes
    -----

    In rsun:

    - extraterrestrial_direct_normal_irradiance is mentioned as `G_norm_extra`
    """

    direct_radiation_coefficient: float
    diffuse_radiation_coefficient: float
    linke_turbidity: float
    extraterrestrial_direct_normal_irradiance: float
    albedo: float


class GridGeometry(BaseModel):
    """
    Represents the grid geometry.

    Attributes:
    - xp: The xp value.
    - yp: The yp value.
    - xx0: The xx0 value.
    - yy0: The yy0 value.
    - xg0: The xg0 value.
    - yg0: The yg0 value.
    - step_x: The step size in the x-direction.
    - step_y: The step size in the y-direction.
    - delta_x: The delta x value.
    - delta_y: The delta y value.
    - step_xy: The step size in the xy-direction.
    - sin_latitude: The sine of latitude.
    - cos_latitude: The cosine of latitude.
    """

    xp: float
    yp: float
    xx0: float
    yy0: float
    xg0: float
    yg0: float
    step_x: float
    step_y: float
    delta_x: float
    delta_y: float
    step_xy: float
    sin_latitude: float
    cos_latitude: float
