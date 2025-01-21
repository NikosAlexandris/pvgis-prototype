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
from pvgisprototype.api.position.models import (
    SolarPositionModel, 
    SolarIncidenceModel, 
    ShadingModel,
    SolarTimeModel,
)

random.seed(22227)
NUMBER_OF_ITERATIONS = 2

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

# Apply atmospheric refraction
APPLY_ATMOSPHERIC_REFRACTION = [random.choice([True, False]) for _ in range(NUMBER_OF_ITERATIONS)]

# Solar Position Models
RANDOM_POSITION_MODELS = [random.choice(list(SolarPositionModel)) for _ in range(NUMBER_OF_ITERATIONS)]
RANDOM_POSITION_MODELS.append(SolarPositionModel.noaa)

NOT_IMPLEMENTED_POSITION_MODELS = [
    SolarPositionModel.hofierka,
    SolarPositionModel.pvlib,
    SolarPositionModel.pysolar,
    SolarPositionModel.skyfield,
    SolarPositionModel.suncalc,
    SolarPositionModel.all,
]

POSITION_MODELS = [
    {
        "model": solar_position_model.value,
        "expected_status_code": 400 if solar_position_model in NOT_IMPLEMENTED_POSITION_MODELS else 200,
    }
    for solar_position_model in RANDOM_POSITION_MODELS
]

# Solar Incidence Models
RANDOM_INCIDENCE_MODELS = [random.choice(list(SolarIncidenceModel)) for _ in range(NUMBER_OF_ITERATIONS)]
RANDOM_INCIDENCE_MODELS.append(SolarIncidenceModel.iqbal)

NOT_IMPLEMENTED_INCIDENCE_MODELS = [
    SolarIncidenceModel.pvis,
    SolarIncidenceModel.all,
]

INCIDENCE_MODELS = [
    {
        "model": solar_incidence_model.value,
        "expected_status_code": 400 if solar_incidence_model in NOT_IMPLEMENTED_INCIDENCE_MODELS else 200,
    }
    for solar_incidence_model in RANDOM_INCIDENCE_MODELS
]

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

# Apply zero negative incidence angle
ZERO_NEGATIVE_SOLAR_INCIDENCE_ANGLE = [random.choice([True, False]) for _ in range(NUMBER_OF_ITERATIONS)]


# Solar time model
RANDOM_SOLAR_TIME_MODELS = [random.choice(list(SolarTimeModel)) for _ in range(NUMBER_OF_ITERATIONS)]
RANDOM_SOLAR_TIME_MODELS.append(SolarTimeModel.milne)
SOLAR_TIME_MODELS = [solar_time_model.value for solar_time_model in RANDOM_SOLAR_TIME_MODELS]

# Angle output unit
RANDOM_ANGLE_OUTPUT_UNITS = [random.choice(list(AngleOutputUnit)) for _ in range(NUMBER_OF_ITERATIONS)]
ANGLE_OUTPUT_UNITS = [angle_output_units.value for angle_output_units in RANDOM_ANGLE_OUTPUT_UNITS]

# CSV
CSV = [random.choice(["ΑΛΕΞΑΝΔΡΟΣ", None, "test"]) for _ in range(NUMBER_OF_ITERATIONS)]

# Verbose
VERBOSE = [random.randint(0, 9) for _ in range(NUMBER_OF_ITERATIONS)]

# Fingerprint
FINGERPRINT = [random.choice([True, False]) for _ in range(NUMBER_OF_ITERATIONS)]

# Generate all combinations
parameter_combinations = product(
    LONGITUDE,
    LATITUDE,
    ELEVATION,
    SURFACE_ORIENTATION,
    SURFACE_TILT,
    DATE_PAIRS,
    TIMEZONES,
    APPLY_ATMOSPHERIC_REFRACTION,
    POSITION_MODELS,
    INCIDENCE_MODELS,
    HORIZON_PROFILE,
    SHADING_MODELS,
    ZERO_NEGATIVE_SOLAR_INCIDENCE_ANGLE,
    SOLAR_TIME_MODELS,
    ANGLE_OUTPUT_UNITS,
    CSV,
    VERBOSE,
    FINGERPRINT,
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
    apply_atmospheric_refraction,
    position_model,
    incidence_model,
    horizon_profile,
    shading_model,
    zero_negative_solar_incidence_angle,
    solar_time_model,
    angle_output_units,
    csv,
    verbose,
    fingerprint,
) in parameter_combinations:
    # Determine the expected status code
    if ((position_model["expected_status_code"] == 400) or 
        (incidence_model["expected_status_code"] == 400) or
        (shading_model["expected_status_code"] == 400)):
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
        "apply_atmospheric_refraction": apply_atmospheric_refraction,
        "solar_position_models": position_model["model"],
        "solar_incidence_model": incidence_model["model"],
        "horizon_profile": horizon_profile,
        "shading_model": shading_model["model"],
        "zero_negative_solar_incidence_angle": zero_negative_solar_incidence_angle,
        "solar_time_model": solar_time_model,
        "angle_output_units": angle_output_units,
        "csv": csv,
        "verbose": verbose,
        "fingerprint": fingerprint,
        "expected_status_code": expected_status_code,
    })

@pytest.mark.parametrize("parameters", parameters_list)
def test_overview(parameters):
    expected_status_code = parameters.pop("expected_status_code")
    response = client.get(
        "/solar-position/overview",
        params=parameters,
    )
    assert response.status_code == expected_status_code
