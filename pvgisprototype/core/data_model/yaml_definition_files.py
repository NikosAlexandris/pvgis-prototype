#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
"""
Important Note !
----------------

The following is an _ordered_ list of files defining PVGIS' native data models
in YAML syntax.

Complex models depend on simpler ones, 
therefore the latter _must exist_ before the former.

If you need to reorder the generation of PVGIS' native data models,
please handle the list with care, as it may lead to issues.

## Hint

When developing new or refactoring existing YAML data model definitions, things
may get messy. To start from scratch, assign an empty dictionary to the
PVGIS_DATA_MODEL_YAML_DEFINITION_FILES "constant", like so

    ```
    PVGIS_DATA_MODEL_YAML_DEFINITION_FILES = {}
    ```
and rerun the script that generates the Python data model definitions.

Happy pv-Hacking !

"""

# Set YAML file extension

YAML_EXTENSION = ".yaml"

# Group YAML files

METADATA_FILES = [
    "metadata/fingerprint",
]

SURFACE_LOCATION_FILES = [
    "surface/location/longitude",
    "surface/location/relative_longitude",
    "surface/location/latitude",
    "surface/location/elevation",
    "surface/location/horizon_height",
    "surface/location/shading",
]

SURFACE_POSITION_FILES = [
    "surface/position/surface_orientation",
    "surface/position/surface_tilt",
    "surface/position/optimal",
]

EARTH_ORBIT_FILES = [
    "earth/eccentricity_phase_offset",
    "earth/eccentricity_amplitude",
]

METEOROLOGICAL_FILES = [
    "meteorology/temperature",
    "meteorology/wind_speed",
]

ATMOSPHERIC_PROPERTIES_FILES = [
    "atmosphere/property/refraction",
    "atmosphere/property/linke_turbidity",
    "atmosphere/property/optical_air_mass",
    "atmosphere/property/rayleigh_thickness",
]

SOLAR_POSITION_FILES = [
    "sun/position/solar_position",
    "sun/time/equation_of_time",
    "sun/time/time_offset",
    "sun/time/true_solar_time",
    "sun/time/solar_hour_angle",
    "sun/time/event_hour_angle",
    "sun/time/event_type",
    "sun/time/event_time",
    "sun/time/hour_angle_sunrise",
    "sun/position/fractional_year",
    "sun/position/solar_declination",
    "sun/position/solar_zenith",
    "sun/position/unrefracted_solar_zenith",
    "sun/position/solar_altitude",
    "sun/position/refracted_solar_altitude",
    "sun/position/solar_azimuth",
    "sun/position/compass_solar_azimuth",
    "sun/position/solar_incidence",
    "sun/position/sun_horizon_position",
    "sun/position/overview",
]

IRRADIANCE_SPECTRUM_FILES = [
    "irradiance/spectrum",
]

PERFORMANCE_FILES = [
    "performance/spectral_responsivity",
    "performance/spectral_factor",
]

IRRADIANCE_FILES = [
    "irradiance/irradiance_series",  # generic irradiance time series data model
    "irradiance/extraterrestrial/normal",
    "irradiance/extraterrestrial/horizontal",
    "irradiance/direct/normal",
    "irradiance/direct/normal_from_horizontal",
    "irradiance/direct/horizontal",
    "irradiance/direct/horizontal_from_external_data",
    "irradiance/direct/inclined",
    "irradiance/direct/inclined_from_external_data",
    "irradiance/diffuse/sky_reflected/horizontal_clear_sky",
    "irradiance/diffuse/sky_reflected/horizontal_from_external_time_series",
    "irradiance/diffuse/sky_reflected/inclined_clear_sky",
    "irradiance/diffuse/sky_reflected/inclined_from_external_time_series",
    "irradiance/global/horizontal",
    "irradiance/diffuse/ground_reflected/inclined_clear_sky",
    "irradiance/diffuse/ground_reflected/inclined_from_external_data",
    "irradiance/global/inclined",
    "irradiance/global/inclined_from_external_data",
    "irradiance/inclined",
    "irradiance/effective",
]

EFFICIENCY_FILES = [
    "performance/efficiency_factor",
    "performance/efficiency",
]

POWER_FILES = [
    "power/photovoltaic",
    "power/photovoltaic_from_external_data",
    "power/photovoltaic_multiple_modules",
]

# Consolidating all files into a single list with the .yaml extension using nested list comprehension
PVGIS_DATA_MODEL_YAML_DEFINITION_FILES = (
    [file + YAML_EXTENSION for group in [
        METADATA_FILES,
        SURFACE_LOCATION_FILES,
        SURFACE_POSITION_FILES,
        EARTH_ORBIT_FILES,
        METEOROLOGICAL_FILES,
        ATMOSPHERIC_PROPERTIES_FILES,
        SOLAR_POSITION_FILES,
        IRRADIANCE_SPECTRUM_FILES,
        PERFORMANCE_FILES,
        IRRADIANCE_FILES,
        EFFICIENCY_FILES,
        POWER_FILES
    ] for file in group]
)
