"""
Important Note !
----------------

The following is an _ordered_ list of files defining PVGIS' native data models
in YAML syntax.

Complex models depend on simpler ones, 
therefore the latter _must exist_ before the former.

If you need to reorder the generation of PVGIS' native data models,
please handle the list with care, as it may lead to issues.

Hint : To start from scratch, especially when things got messy, assign an empty
dictionary to the PVGIS_DATA_MODEL_YAML_DEFINITION_FILES.

Happy pv-Hacking !
"""

# Base YAML file extension
YAML_EXTENSION = ".yaml"

# Grouping related files for better organization
LOCATION_FILES = [
    "location/longitude",
    "location/relative_longitude",
    "location/latitude",
    "location/elevation",
    "location/horizon_height",
    "location/shading",
]

SURFACE_POSITION_FILES = [
    "surface_position/surface_orientation",
    "surface_position/surface_tilt",
]

EARTH_ORBIT_FILES = [
    "solar_position/eccentricity_phase_offset",
    "solar_position/eccentricity_amplitude",
]

METEOROLOGICAL_FILES = [
    "meteorological_variables/temperature",
    "meteorological_variables/wind_speed",
]

ATMOSPHERIC_PROPERTIES_FILES = [
    "atmospheric_properties/atmospheric_refraction",
    "atmospheric_properties/linke_turbidity",
    "atmospheric_properties/optical_air_mass",
    "atmospheric_properties/rayleigh_thickness",
]

SOLAR_POSITION_FILES = [
    "solar_position/solar_position",
    "solar_position/equation_of_time",
    "solar_position/time_offset",
    "solar_position/true_solar_time",
    "solar_position/solar_hour_angle",
    "solar_position/event_hour_angle",
    "solar_position/event_time",
    "solar_position/hour_angle_sunrise",
    "solar_position/fractional_year",
    "solar_position/solar_declination",
    "solar_position/solar_zenith",
    "solar_position/refracted_solar_zenith",
    "solar_position/solar_altitude",
    "solar_position/refracted_solar_altitude",
    "solar_position/solar_azimuth",
    "solar_position/compass_solar_azimuth",
    "solar_position/solar_incidence",
]

IRRADIANCE_SPECTRUM_FILES = [
    "irradiance/spectrum",
]

PERFORMANCE_FILES = [
    "performance/spectral_responsivity",
    "performance/spectral_factor",
]

IRRADIANCE_FILES = [
    "irradiance/irradiance",
    "irradiance/extraterrestrial/normal",
    "irradiance/extraterrestrial/horizontal",
    "irradiance/direct/normal",
    "irradiance/direct/normal_from_horizontal",
    "irradiance/direct/horizontal",
    "irradiance/direct/horizontal_from_external_data",
    "irradiance/direct/inclined",
    "irradiance/direct/inclined_from_external_data",
    "irradiance/diffuse/sky_reflected/horizontal",
    "irradiance/diffuse/sky_reflected/horizontal_from_external_time_series",
    "irradiance/diffuse/sky_reflected/inclined",
    "irradiance/diffuse/sky_reflected/inclined_from_external_time_series",
    "irradiance/global/horizontal",
    "irradiance/diffuse/ground_reflected/inclined",
    "irradiance/diffuse/ground_reflected/inclined_from_external_data",
    "irradiance/global/inclined",
    "irradiance/global/inclined_from_external_data",
    "irradiance/inclined",
    "irradiance/effective",
]

EFFICIENCY_FILES = [
    "performance/efficiency",
]

POWER_FILES = [
    "power/photovoltaic",
    "power/photovoltaic_from_external_data",
    "power/photovoltaic_multiple_modules",
]

# Consolidating all files into a single list with the .yaml extension using nested list comprehension
PVGIS_DATA_MODEL_YAML_DEFINITION_FILES = (
    ["fields/fingerprint" + YAML_EXTENSION] +
    [file + YAML_EXTENSION for group in [
        LOCATION_FILES,
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
