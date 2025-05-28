import random
from datetime import datetime

from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.position.models import ShadingModel
from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.web_api.schemas import AnalysisLevel, AngleOutputUnit, Timezone

from .utilities import generate_random_date_pair, validate_time

random.seed(22227)
NUMBER_OF_TESTS = 20000


def generate_cases_solar_performance_broadband(number_of_tests=NUMBER_OF_TESTS):
    """Generate random combinations of parameters."""
    # Constants for random sampling
    longitude = [8.628]
    latitude = [45.812]
    elevation_range = (200, 250)
    surface_orientation_range = (0, 360)
    surface_tilt_range = (0, 180)
    date_range_start = datetime(2005, 1, 1)
    date_range_end = datetime(2020, 12, 31)
    timezones = [timezone.value for timezone in Timezone]
    horizon_profile_choices = ["PVGIS", "80,80,80,80", "0,0,0,0", "10,20,30,40"]
    shading_models = [shading_model for shading_model in ShadingModel]
    not_implemented_shading_models = [ShadingModel.all, ShadingModel.pvlib]
    photovoltaic_module_models = [module.value for module in PhotovoltaicModuleModel]
    system_efficiency_range = (0, 1)
    power_models = [model.value for model in PhotovoltaicModulePerformanceModel]
    peak_power_range = (0, 10)
    angle_output_units = [unit.value for unit in AngleOutputUnit]
    analysis_levels = [level.value for level in AnalysisLevel]
    csv_choices = [None, "test", "ΑΛΕΞΑΝΔΡΟΣ"]
    boolean_choices = [True, False]
    verbose_range = (0, 9)

    for _ in range(number_of_tests):
        expected_status_code = 200

        # Generate random values for the parameters
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

        # Yield a single test case
        yield (
            {
                "longitude": random.choice(longitude),
                "latitude": random.choice(latitude),
                "elevation": random.randint(*elevation_range),
                "surface_orientation": random.uniform(*surface_orientation_range),
                "surface_tilt": random.uniform(*surface_tilt_range),
                "start_time": start_date,
                "end_time": end_date,
                "timezone": timezone,
                "horizon_profile": random.choice(horizon_profile_choices),
                "shading_model": shading_model.value,
                "photovoltaic_module": random.choice(photovoltaic_module_models),
                "system_efficiency": random.uniform(*system_efficiency_range),
                "power_model": random.choice(power_models),
                "peak_power": random.randint(*peak_power_range),
                "angle_output_units": random.choice(angle_output_units),
                "analysis": random.choice(analysis_levels),
                "csv": random.choice(csv_choices),
                "verbose": random.randint(*verbose_range),
                "index": random.choice(boolean_choices),
                "quiet": random.choice(boolean_choices),
                "fingerprint": random.choice(boolean_choices),
                "quick_response_code": random.choice(
                    [code.value for code in QuickResponseCode]
                ),
                "metadata": random.choice(boolean_choices),
            },
            expected_status_code,
        )
