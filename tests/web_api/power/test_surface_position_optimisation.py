import random
from datetime import datetime, timedelta
import pytest
from pandas import Timestamp
from zoneinfo import ZoneInfo
from pytz import NonExistentTimeError
from fastapi.testclient import TestClient
from pvgisprototype.webapi import app
from pvgisprototype.web_api.schemas import Timezone, AngleOutputUnit
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.position.models import ShadingModel
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerModeWithoutNone,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
)

random.seed(22227)
NUMBER_OF_TESTS = 20000

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
LINKE_TURBIDITY_RANGE = (0,8)
HORIZON_PROFILE_CHOICES = ["PVGIS", "80,80,80,80", "0,0,0,0", "10,20,30,40"]
SHADING_MODELS = [shading_model for shading_model in ShadingModel]
NOT_IMPLEMENTED_SHADING_MODELS = [ShadingModel.all, ShadingModel.pvlib]
PHOTOVOLTAIC_MODULE_MODELS = [module.value for module in PhotovoltaicModuleModel]
ANGLE_OUTPUT_UNITS = [unit.value for unit in AngleOutputUnit]
BOOLEAN_CHOICES = [True, False]
VERBOSE_RANGE = (0, 9)
OPTIMIZE_SURFACE_POSITION = [optimise_surface_position.value for optimise_surface_position in SurfacePositionOptimizerModeWithoutNone]
SAMPLING_METHOD = [sampling_method.value for sampling_method in SurfacePositionOptimizerMethodSHGOSamplingMethod]

def validate_time(datetime_object, timezone):
    """Check if a datetime is valid in the given timezone."""
    try:
        Timestamp(datetime_object, tz=ZoneInfo(timezone))  # Force timezone localization
        return True
    except NonExistentTimeError:
        return False

def generate_random_date_pair(start, end):
    """Generate a random start_date and end_date such that start_date < end_date."""
    start_date = start + timedelta(days=random.randint(0, (end - start).days))
    
    # Ensure there is at least one valid day for the end_date
    if start_date >= end:
        return start_date, start_date + timedelta(days=1)
    
    end_date = start_date + timedelta(days=random.randint(1, (end - start_date).days))
    return start_date, end_date


def remove_none_values(parameters):
    """Remove keys with None values from the parameters dictionary."""
    return {key: value for key, value in parameters.items() if value is not None}


# Generate random test cases
parameters_list = []
for _ in range(NUMBER_OF_TESTS):
    expected_status_code = 200

    start_date, end_date = generate_random_date_pair(DATE_RANGE_START, DATE_RANGE_END)
    timezone = random.choice(TIMEZONES)
    if not validate_time(start_date, timezone) or not validate_time(end_date, timezone):
        expected_status_code = 400

    shading_model = random.choice(SHADING_MODELS)
    if shading_model in NOT_IMPLEMENTED_SHADING_MODELS:
        expected_status_code = 400

    parameters = {
        "longitude": random.choice(LONGITUDE),
        "latitude": random.choice(LATITUDE),
        "elevation": random.randint(*ELEVATION_RANGE),
        "surface_orientation": random.uniform(*SURFACE_ORIENTATION_RANGE),
        "surface_tilt": random.uniform(*SURFACE_TILT_RANGE),
        "start_time": start_date,
        "end_time": end_date,
        "timezone": random.choice(TIMEZONES),
        "linke_turbidity_factor_series": random.uniform(*LINKE_TURBIDITY_RANGE),
        "horizon_profile": random.choice(HORIZON_PROFILE_CHOICES),
        "shading_model": shading_model.value,
        "photovoltaic_module": random.choice(PHOTOVOLTAIC_MODULE_MODELS),
        "angle_output_units": random.choice(ANGLE_OUTPUT_UNITS),
        "verbose": random.randint(*VERBOSE_RANGE),
        "optimise_surface_position": random.choice(OPTIMIZE_SURFACE_POSITION),
        "sampling_method_shgo": random.choice(SAMPLING_METHOD),
        "expected_status_code": expected_status_code,
    }
    
    # Remove keys with None values
    parameters = remove_none_values(parameters)
    parameters_list.append(parameters)



@pytest.mark.parametrize("parameters", parameters_list)
def test_status(parameters):
    expected_status_code = parameters.pop("expected_status_code")
    print("-----------------------")
    print(f"{parameters=}")
    response = client.get(
        "/power/surface-position-optimisation",
        params=parameters,
    )
    print(f"{response.text=}")
    assert response.status_code == expected_status_code
    print("-----------------------")