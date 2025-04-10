from pathlib import Path
from definition_factory import (
    build_python_data_models,
    write_to_python_module,
)

# _Ordered_ list of data model definitions in YAML syntax.
# Note that some data models depend on others !

PVGIS_DATA_MODEL_YAML_DEFINITIONS = [
    "longitude.yaml",
    "relative_longitude.yaml",
    "latitude.yaml",
    "elevation.yaml",
    "horizon_height.yaml",
    "shading.yaml",
    "surface_orientation.yaml",
    "surface_tilt.yaml",
    "perigee_offset.yaml",
    "eccentricity_correction_factor.yaml",
    "temperature.yaml",
    "wind_speed.yaml",
    "atmospheric_refraction.yaml",
    "linke_turbidity.yaml",
    "optical_air_mass.yaml",
    "rayleigh_thickness.yaml",
    "solar_position.yaml",
    "equation_of_time.yaml",
    "time_offset.yaml",
    "true_solar_time.yaml",
    "solar_hour_angle.yaml",
    "event_hour_angle.yaml",
    "event_time.yaml",
    "hour_angle_sunrise.yaml",
    "fractional_year.yaml",
    "solar_declination.yaml",
    "solar_zenith.yaml",
    "refracted_solar_zenith.yaml",
    "solar_altitude.yaml",
    "refracted_solar_altitude.yaml",
    "solar_azimuth.yaml",
    "compass_solar_azimuth.yaml",
    "solar_incidence.yaml",
    "solar_irradiance_spectrum.yaml",
    "spectral_responsivity.yaml",
    "spectral_factor.yaml",
    "irradiance.yaml",
    "extraterrestrial_irradiance.yaml",
    "normal_irradiance.yaml",
    "ground_reflected_irradiance.yaml",
    "ground_reflected_inclined_irradiance.yaml",
    "direct_irradiance.yaml",
    "sky_reflected_irradiance.yaml",
    "inclined_irradiance.yaml",
    "effective_irradiance.yaml",
    "efficiency.yaml",
    "photovoltaic_power.yaml",
    "photovoltaic_power_multiple_modules.yaml",
]

def main(
    source_path: Path = Path("definitions"),
    definitions: list = PVGIS_DATA_MODEL_YAML_DEFINITIONS,
    output_file: Path = Path("data_model_definitions.py"),
):
    """ """
    pvgis_data_models = build_python_data_models(
        source_path=source_path,
        yaml_files=definitions,
    )
    write_to_python_module(models=pvgis_data_models, output_file=output_file)

if __name__ == "__main__":
    main()
