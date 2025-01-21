import random
from itertools import product
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from pvgisprototype.webapi import app
from pvgisprototype.web_api.schemas import (
    Timezone,
    AngleOutputUnit,
)
from pvgisprototype.web_api.schemas import AnalysisLevel
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.api.position.models import ShadingModel

random.seed(22227)
NUMBER_OF_ITERATIONS = 3

client = TestClient(app)

# Define the variables
LONGITUDE = [8.628]
LATITUDE = [45.812]
ELEVATION = [random.randint(200, 250) for _ in range(NUMBER_OF_ITERATIONS)]
SURFACE_ORIENTATION = [random.uniform(0, 360) for _ in range(NUMBER_OF_ITERATIONS)]
SURFACE_TILT = [random.uniform(0, 180) for _ in range(NUMBER_OF_ITERATIONS)]

# Define the date range for generating random date pairs
date_range_start = datetime(2005, 1, 1)
date_range_end = datetime(2020, 12, 31)

def generate_random_date_pair(start, end):
    """Generate a random start_date and end_date such that start_date < end_date."""
    start_date = start + timedelta(days=random.randint(0, (end - start).days))
    end_date = start_date + timedelta(days=random.randint(1, (end - start_date).days))
    return start_date, end_date

# Randomly generate DATE_PAIRS
DATE_PAIRS = [
    generate_random_date_pair(date_range_start, date_range_end)
    for _ in range(NUMBER_OF_ITERATIONS)
]

# Randomly add timezones, plus UTC always
RANDOM_TIMEZONES = [random.choice(list(Timezone)) for _ in range(NUMBER_OF_ITERATIONS)]
RANDOM_TIMEZONES.append(Timezone.UTC)  # type: ignore[attr-defined]
TIMEZONES = [timezone.value for timezone in RANDOM_TIMEZONES]

# Horizon profile
HORIZON_PROFILE_CHOICES = ["PVGIS", "80,80,80,80", "0,0,0,0", "10,20,30,40"]
HORIZON_PROFILE = [random.choice(HORIZON_PROFILE_CHOICES) for _ in range(NUMBER_OF_ITERATIONS)]

# Shading model
NOT_IMPLEMENTED_SHADING_MODEL = [
        ShadingModel.all,
        ShadingModel.pvlib,
    ]

RANDOM_SHADING_MODELS = [random.choice(list(ShadingModel)) for _ in range(NUMBER_OF_ITERATIONS)]
RANDOM_SHADING_MODELS.append(ShadingModel.pvis)

SHADING_MODELS = [
    {
        "model": shading_model.value,
        "expected_status_code": 400 if shading_model in NOT_IMPLEMENTED_SHADING_MODEL else 200,
    }
    for shading_model in RANDOM_SHADING_MODELS
]

RANDOM_PHOTOVOLTAIC_MODULE_MODELS = [random.choice(list(PhotovoltaicModuleModel)) for _ in range(NUMBER_OF_ITERATIONS)]
PHOTOVOLTAIC_MODULE_MODELS = [photovoltaic_module.value for photovoltaic_module in RANDOM_PHOTOVOLTAIC_MODULE_MODELS]

SYSTEM_EFFICIENCY = [random.uniform(0, 1) for _ in range(NUMBER_OF_ITERATIONS)]
SYSTEM_EFFICIENCY.append(0.86)

RANDOM_POWER_MODELS = [random.choice(list(PhotovoltaicModulePerformanceModel)) for _ in range(NUMBER_OF_ITERATIONS)]
RANDOM_POWER_MODELS.append(PhotovoltaicModulePerformanceModel.king)
POWER_MODELS = [power_model.value for power_model in RANDOM_POWER_MODELS]


PEAK_POWER = [random.randint(0, 10) for _ in range(NUMBER_OF_ITERATIONS)]

# Angle output unit
RANDOM_ANGLE_OUTPUT_UNITS = [random.choice(list(AngleOutputUnit)) for _ in range(NUMBER_OF_ITERATIONS)]
ANGLE_OUTPUT_UNITS = [angle_output_units.value for angle_output_units in RANDOM_ANGLE_OUTPUT_UNITS]

RANDOM_ANALYSIS = [random.choice(list(AnalysisLevel)) for _ in range(NUMBER_OF_ITERATIONS)]
ANALYSIS = [analysis.value for analysis in RANDOM_ANALYSIS]

# CSV
CSV = [random.choice(["ΑΛΕΞΑΝΔΡΟΣ", None, "test"]) for _ in range(NUMBER_OF_ITERATIONS)]

# Verbose
VERBOSE = [random.randint(0, 9) for _ in range(NUMBER_OF_ITERATIONS)]

INDEX = [random.choice([True, False]) for _ in range(NUMBER_OF_ITERATIONS)]

QUIET = [random.choice([True, False]) for _ in range(NUMBER_OF_ITERATIONS)]

FINGERPRINT = [random.choice([True, False]) for _ in range(NUMBER_OF_ITERATIONS)]

RANDOM_QUICK_RESPONSE_CODE = [random.choice(list(QuickResponseCode)) for _ in range(NUMBER_OF_ITERATIONS)]
RANDOM_QUICK_RESPONSE_CODE.append(QuickResponseCode.NoneValue)

QUICK_RESPONSE_CODE = [quick_response_code.value for quick_response_code in RANDOM_QUICK_RESPONSE_CODE]

METADATA = [random.choice([True, False]) for _ in range(NUMBER_OF_ITERATIONS)]

# Generate all combinations
parameter_combinations = product(
    LONGITUDE,
    LATITUDE,
    ELEVATION,
    SURFACE_ORIENTATION,
    SURFACE_TILT,
    DATE_PAIRS,
    TIMEZONES,
    HORIZON_PROFILE,
    SHADING_MODELS,
    PHOTOVOLTAIC_MODULE_MODELS,
    SYSTEM_EFFICIENCY,
    POWER_MODELS,
    PEAK_POWER,
    ANGLE_OUTPUT_UNITS,
    ANALYSIS,
    CSV,
    VERBOSE,
    INDEX,
    QUIET,
    FINGERPRINT,
    QUICK_RESPONSE_CODE,
    METADATA,
)

# Store combinations as dictionaries
parameters_list = []
for (
    longitude,
    latitude,
    elevation,
    surface_orientation,
    surface_tilt,
    (start_date, end_date),
    timezone,
    horizon_profile,
    shading_model,
    photovoltaic_module,
    system_efficiency,
    power_model,
    peak_power,
    angle_output_units,
    analysis,
    csv,
    verbose,
    index,
    quiet,
    fingerprint,
    quick_response_code,
    metadata,
) in parameter_combinations:
    # Determine the expected status code
    if ((shading_model["expected_status_code"] == 400)):
        expected_status_code = 400
    else:
        expected_status_code = 200

    parameters_list.append({
        "longitude": longitude,
        "latitude": latitude,
        "elevation": elevation,
        "surface_orientation": surface_orientation,
        "surface_tilt": surface_tilt,
        "start_time": start_date.strftime("%Y-%m-%d"),  # Convert to string for query parameters
        "end_time": end_date.strftime("%Y-%m-%d"),      # Convert to string for query parameters
        "timezone": timezone,
        "horizon_profile": horizon_profile,
        "shading_model": shading_model["model"],
        "photovoltaic_module": photovoltaic_module,
        "power_model": power_model,
        "peak-power": peak_power,
        "angle_output_units": angle_output_units,
        "analysis": analysis,
        "csv": csv,
        "verbose": verbose,
        "index": index,
        "quiet": quiet,
        "fingerprint": fingerprint,
        "quick_response_code": quick_response_code,
        "metadata": metadata,
        "expected_status_code": expected_status_code,
    })

@pytest.mark.parametrize("parameters", parameters_list)
def test_overview(parameters):
    expected_status_code = parameters.pop("expected_status_code")
    response = client.get(
        "/performance/broadband",
        params=parameters,
    )
    assert response.status_code == expected_status_code
