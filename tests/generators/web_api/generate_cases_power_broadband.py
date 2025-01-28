import random
from datetime import datetime

from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import (
    ShadingModel,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.web_api.schemas import AngleOutputUnit, GroupBy, Timezone

from .utilities import generate_random_date_pair, remove_none_values, validate_time

random.seed(22227)
NUMBER_OF_TESTS = 20000


def generate_cases_power_broadband(number_of_tests=NUMBER_OF_TESTS):

    # Define the ranges and choices for random sampling
    longitude = [8.628]
    latitude = [45.812]
    elevation_range = (200, 250)
    surface_orientation_range = (0, 360)
    surface_tilt_range = (0, 180)
    date_range_start = datetime(2005, 1, 1)
    date_range_end = datetime(2020, 12, 31)
    timezones = [timezone.value for timezone in Timezone]
    neighbor_lookup = [method.value for method in MethodForInexactMatches]
    tolerance_range = (0.1, 0.5)
    linke_turbidity_range = (0, 8)
    refracted_solar_zenith = [90.833]
    albedo_range = (0, 1)
    solar_position_models = [
        solar_position_model.value for solar_position_model in SolarPositionModel
    ]
    not_implemented_position_models = [
        SolarPositionModel.hofierka,
        SolarPositionModel.pvlib,
        SolarPositionModel.pysolar,
        SolarPositionModel.skyfield,
        SolarPositionModel.suncalc,
        SolarPositionModel.all,
    ]
    solar_incidence_models = [
        solar_incidence_model.value for solar_incidence_model in SolarIncidenceModel
    ]
    not_implemented_incidence_models = [
        SolarIncidenceModel.pvis,
        SolarIncidenceModel.all,
    ]
    horizon_profile_choices = ["PVGIS", "80,80,80,80", "0,0,0,0", "10,20,30,40"]
    shading_models = [shading_model for shading_model in ShadingModel]
    not_implemented_shading_models = [ShadingModel.all, ShadingModel.pvlib]
    solar_time_models = [solar_time_model.value for solar_time_model in SolarTimeModel]
    solar_constant = [1360.8]
    perigee_offset = [0.048869]
    eccentricity_correction_factor = [0.03344]
    photovoltaic_module_models = [module.value for module in PhotovoltaicModuleModel]
    system_efficiency_range = (0, 1)
    power_models = [model.value for model in PhotovoltaicModulePerformanceModel]
    peak_power_range = (0, 10)
    temperature_models = [model.value for model in ModuleTemperatureAlgorithm]
    radiation_cutoff_threshold = [0]
    efficiency = [None, 0.67]
    angle_output_units = [unit.value for unit in AngleOutputUnit]
    groupby = [groupby.value for groupby in GroupBy]
    csv_choices = [None, "test", "ΑΛΕΞΑΝΔΡΟΣ"]
    boolean_choices = [True, False]
    verbose_range = (0, 9)
    optimize_surface_position = [
        optimise_surface_position.value
        for optimise_surface_position in SurfacePositionOptimizerMode
    ]
    sampling_method = [
        sampling_method.value
        for sampling_method in SurfacePositionOptimizerMethodSHGOSamplingMethod
    ]

    for _ in range(number_of_tests):
        expected_status_code = 200

        start_date, end_date = generate_random_date_pair(
            date_range_start, date_range_end
        )
        timezone = random.choice(timezones)
        if not validate_time(start_date, timezone) or not validate_time(
            end_date, timezone
        ):
            expected_status_code = 400

        shading_model = random.choice(shading_models)
        if shading_model in not_implemented_shading_models:
            expected_status_code = 400

        solar_position_model = random.choice(solar_position_models)
        if solar_position_model in not_implemented_position_models:
            expected_status_code = 400

        solar_incidence_model = random.choice(solar_incidence_models)
        if solar_incidence_model in not_implemented_incidence_models:
            expected_status_code = 400

        effieciency = random.choice(efficiency)
        if effieciency is not None:
            effieciency = float(effieciency)

        parameters = remove_none_values(
            {
                "longitude": random.choice(longitude),
                "latitude": random.choice(latitude),
                "elevation": random.randint(*elevation_range),
                "surface_orientation": random.uniform(*surface_orientation_range),
                "surface_tilt": random.uniform(*surface_tilt_range),
                "start_time": start_date,
                "end_time": end_date,
                "timezone": random.choice(timezones),
                "neighbor_lookup": random.choice(neighbor_lookup),
                "tolerance": random.uniform(*tolerance_range),
                "mask_and_scale": random.choice(boolean_choices),
                "in_memory": random.choice(boolean_choices),
                "linke_turbidity_factor_series": random.uniform(*linke_turbidity_range),
                "apply_atmospheric_refraction": random.choice(boolean_choices),
                "refracted_solar_zenith": random.choice(refracted_solar_zenith),
                "albedo": random.uniform(*albedo_range),
                "apply_reflectivity_factor": random.choice(boolean_choices),
                "solar_position_model": solar_position_model,
                "solar_incidence_model": solar_incidence_model,
                "horizon_profile": random.choice(horizon_profile_choices),
                "shading_model": shading_model.value,
                "zero_negative_solar_incidence_angle": random.choice(boolean_choices),
                "solar_time_model": random.choice(solar_time_models),
                "solar_constant": random.choice(solar_constant),
                "perigee_offset": random.choice(perigee_offset),
                "eccentricity_correction_factor": random.choice(
                    eccentricity_correction_factor
                ),
                "photovoltaic_module": random.choice(photovoltaic_module_models),
                "system_efficiency": random.uniform(*system_efficiency_range),
                "power_model": random.choice(power_models),
                "peak_power": random.randint(*peak_power_range),
                "temperature_model": random.choice(temperature_models),
                "radiation_cutoff_threshold": random.choice(radiation_cutoff_threshold),
                "efficiency": effieciency,
                "angle_output_units": random.choice(angle_output_units),
                "statistics": random.choice(boolean_choices),
                "groupby": random.choice(groupby),
                "csv": random.choice(csv_choices),
                "verbose": random.randint(*verbose_range),
                "quiet": random.choice(boolean_choices),
                "fingerprint": random.choice(boolean_choices),
                "quick_response_code": random.choice(
                    [code.value for code in QuickResponseCode]
                ),
                "optimise_surface_position": random.choice(optimize_surface_position),
                "sampling_method_shgo": random.choice(sampling_method),
            }
        )

        yield (parameters, expected_status_code)
