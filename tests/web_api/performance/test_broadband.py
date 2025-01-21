import random
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from pvgisprototype.webapi import app
from pvgisprototype.web_api.schemas import Timezone, AngleOutputUnit
from pvgisprototype.web_api.schemas import AnalysisLevel
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.api.position.models import ShadingModel

random.seed(22227)
NUMBER_OF_TESTS = 10000

client = TestClient(app)

# Define the ranges and choices for random sampling
LONGITUDE = [8.628]
LATITUDE = [45.812]
ELEVATION_RANGE = (200, 250)
SURFACE_ORIENTATION_RANGE = (0, 360)
SURFACE_TILT_RANGE = (0, 180)
DATE_RANGE_START = datetime(2005, 1, 1)
DATE_RANGE_END = datetime(2020, 12, 31)
TIMEZONES = [timezone.value for timezone in Timezone]
HORIZON_PROFILE_CHOICES = ["PVGIS", "80,80,80,80", "0,0,0,0", "10,20,30,40"]
SHADING_MODELS = [shading_model for shading_model in ShadingModel]
NOT_IMPLEMENTED_SHADING_MODELS = [ShadingModel.all, ShadingModel.pvlib]
PHOTOVOLTAIC_MODULE_MODELS = [module.value for module in PhotovoltaicModuleModel]
SYSTEM_EFFICIENCY_RANGE = (0, 1)
POWER_MODELS = [model.value for model in PhotovoltaicModulePerformanceModel]
PEAK_POWER_RANGE = (0, 10)
ANGLE_OUTPUT_UNITS = [unit.value for unit in AngleOutputUnit]
ANALYSIS_LEVELS = [level.value for level in AnalysisLevel]
CSV_CHOICES = [None, "test"]
BOOLEAN_CHOICES = [True, False]
VERBOSE_RANGE = (0, 9)

def generate_random_date_pair(start, end):
    """Generate a random start_date and end_date such that start_date < end_date."""
    start_date = start + timedelta(days=random.randint(0, (end - start).days))
    
    # Ensure there is at least one valid day for the end_date
    if start_date >= end:
        return start_date, start_date + timedelta(days=1)
    
    end_date = start_date + timedelta(days=random.randint(1, (end - start_date).days))
    return start_date, end_date

# Generate random test cases
parameters_list = []
for _ in range(NUMBER_OF_TESTS):
    start_date, end_date = generate_random_date_pair(DATE_RANGE_START, DATE_RANGE_END)
    shading_model = random.choice(SHADING_MODELS)
    expected_status_code = 400 if shading_model in NOT_IMPLEMENTED_SHADING_MODELS else 200

    parameters_list.append({
        "longitude": random.choice(LONGITUDE),
        "latitude": random.choice(LATITUDE),
        "elevation": random.randint(*ELEVATION_RANGE),
        "surface_orientation": random.uniform(*SURFACE_ORIENTATION_RANGE),
        "surface_tilt": random.uniform(*SURFACE_TILT_RANGE),
        "start_time": start_date,
        "end_time": end_date,
        "timezone": random.choice(TIMEZONES),
        "horizon_profile": random.choice(HORIZON_PROFILE_CHOICES),
        "shading_model": shading_model.value,
        "photovoltaic_module": random.choice(PHOTOVOLTAIC_MODULE_MODELS),
        "system_efficiency": random.uniform(*SYSTEM_EFFICIENCY_RANGE),
        "power_model": random.choice(POWER_MODELS),
        "peak_power": random.randint(*PEAK_POWER_RANGE),
        "angle_output_units": random.choice(ANGLE_OUTPUT_UNITS),
        "analysis": random.choice(ANALYSIS_LEVELS),
        "csv": random.choice(CSV_CHOICES),
        "verbose": random.randint(*VERBOSE_RANGE),
        "index": random.choice(BOOLEAN_CHOICES),
        "quiet": random.choice(BOOLEAN_CHOICES),
        "fingerprint": random.choice(BOOLEAN_CHOICES),
        "quick_response_code": random.choice([code.value for code in QuickResponseCode]),
        "metadata": random.choice(BOOLEAN_CHOICES),
        "expected_status_code": expected_status_code,
    })

# Parametrize test function
@pytest.mark.parametrize("parameters", parameters_list)
def test_status(parameters):
    expected_status_code = parameters.pop("expected_status_code")
    print("-----------------------")
    print(f"{parameters=}")
    response = client.get(
        "/performance/broadband",
        params=parameters,
    )
    assert response.status_code == expected_status_code
    print("-----------------------")

