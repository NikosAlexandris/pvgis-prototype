import random
from datetime import datetime, timedelta
import pytest
from pandas import Timestamp
from zoneinfo import ZoneInfo
from pytz import NonExistentTimeError
from fastapi.testclient import TestClient
from pvgisprototype.webapi import app
from pvgisprototype.web_api.schemas import Timezone, AngleOutputUnit
from pvgisprototype.web_api.schemas import AnalysisLevel
from pvgisprototype.web_api.schemas import GroupBy
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.performance.models import PhotovoltaicModulePerformanceModel
from pvgisprototype.api.quick_response_code import QuickResponseCode
from pvgisprototype.api.position.models import ShadingModel
from pvgisprototype.api.irradiance.models import (
    MethodForInexactMatches,
    ModuleTemperatureAlgorithm,
)
from pvgisprototype.api.position.models import (
    SolarPositionModel,
    SolarIncidenceModel,
    SolarTimeModel,
)
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMode,
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
NEIGHBOR_LOOKUP = [method.value for method in MethodForInexactMatches]
TOLERANCE_RANGE = (0.1, 0.5)
LINKE_TURBIDITY_RANGE = (0,8)
REFRACTED_SOLAR_ZENITH = [90.833]
ALBEDO_RANGE = (0, 1)
SOLAR_POSITION_MODELS = [solar_position_model.value for solar_position_model in SolarPositionModel]
NOT_IMPLEMENTED_POSITION_MODELS = [
    SolarPositionModel.hofierka,
    SolarPositionModel.pvlib,
    SolarPositionModel.pysolar,
    SolarPositionModel.skyfield,
    SolarPositionModel.suncalc,
    SolarPositionModel.all,
]
SOLAR_INCIDENCE_MODELS = [solar_incidence_model.value for solar_incidence_model in SolarIncidenceModel]
NOT_IMPLEMENTED_INCIDENCE_MODELS = [
    SolarIncidenceModel.pvis,
    SolarIncidenceModel.all,
]
HORIZON_PROFILE_CHOICES = ["PVGIS", "80,80,80,80", "0,0,0,0", "10,20,30,40"]
SHADING_MODELS = [shading_model for shading_model in ShadingModel]
NOT_IMPLEMENTED_SHADING_MODELS = [ShadingModel.all, ShadingModel.pvlib]
SOLAR_TIME_MODELS = [solar_time_model.value for solar_time_model in SolarTimeModel]
SOLAR_CONSTANT = [1360.8]
PERIGEE_OFFSET = [0.048869]
ECCENTRICITY_CORRECTION_FACTOR = [0.03344]
PHOTOVOLTAIC_MODULE_MODELS = [module.value for module in PhotovoltaicModuleModel]
SYSTEM_EFFICIENCY_RANGE = (0, 1)
POWER_MODELS = [model.value for model in PhotovoltaicModulePerformanceModel]
PEAK_POWER_RANGE = (0, 10)
TEMPERATURE_MODELS = [model.value for model in ModuleTemperatureAlgorithm]
RADIATION_CUTOFF_THRESHOLD = [0]
EFFICIENCY = [None, 0.67]
ANGLE_OUTPUT_UNITS = [unit.value for unit in AngleOutputUnit]
GROUPBY = [groupby.value for groupby in GroupBy]
ANALYSIS_LEVELS = [level.value for level in AnalysisLevel]
CSV_CHOICES = [None, "test", "ΑΛΕΞΑΝΔΡΟΣ"]
BOOLEAN_CHOICES = [True, False]
VERBOSE_RANGE = (0, 9)
OPTIMIZE_SURFACE_POSITION = [optimise_surface_position.value for optimise_surface_position in SurfacePositionOptimizerMode]
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

    solar_position_model = random.choice(SOLAR_POSITION_MODELS)
    if solar_position_model in NOT_IMPLEMENTED_POSITION_MODELS:
        expected_status_code = 400 

    solar_incidence_model= random.choice(SOLAR_INCIDENCE_MODELS)
    if solar_incidence_model in NOT_IMPLEMENTED_INCIDENCE_MODELS:
        expected_status_code = 400
    
    effieciency = random.choice(EFFICIENCY)
    if effieciency is not None:
        effieciency = float(effieciency)
    
    parameters = {
        "longitude": random.choice(LONGITUDE),
        "latitude": random.choice(LATITUDE),
        "elevation": random.randint(*ELEVATION_RANGE),
        "surface_orientation": random.uniform(*SURFACE_ORIENTATION_RANGE),
        "surface_tilt": random.uniform(*SURFACE_TILT_RANGE),
        "start_time": start_date,
        "end_time": end_date,
        "timezone": random.choice(TIMEZONES),
        "neighbor_lookup": random.choice(NEIGHBOR_LOOKUP),
        "tolerance": random.uniform(*TOLERANCE_RANGE),
        "mask_and_scale": random.choice(BOOLEAN_CHOICES),
        "in_memory": random.choice(BOOLEAN_CHOICES),
        "linke_turbidity_factor_series": random.uniform(*LINKE_TURBIDITY_RANGE),
        "apply_atmospheric_refraction": random.choice(BOOLEAN_CHOICES),
        "refracted_solar_zenith": random.choice(REFRACTED_SOLAR_ZENITH),
        "albedo": random.uniform(*ALBEDO_RANGE),
        "apply_reflectivity_factor": random.choice(BOOLEAN_CHOICES),
        "solar_position_model": solar_position_model,
        "solar_incidence_model": solar_incidence_model,
        "horizon_profile": random.choice(HORIZON_PROFILE_CHOICES),
        "shading_model": shading_model.value,
        "zero_negative_solar_incidence_angle": random.choice(BOOLEAN_CHOICES),
        "solar_time_model": random.choice(SOLAR_TIME_MODELS),
        "solar_constant": random.choice(SOLAR_CONSTANT),
        "perigee_offset": random.choice(PERIGEE_OFFSET),
        "eccentricity_correction_factor": random.choice(ECCENTRICITY_CORRECTION_FACTOR),
        "photovoltaic_module": random.choice(PHOTOVOLTAIC_MODULE_MODELS),
        "system_efficiency": random.uniform(*SYSTEM_EFFICIENCY_RANGE),
        "power_model": random.choice(POWER_MODELS),
        "peak_power": random.randint(*PEAK_POWER_RANGE),
        "temperature_model": random.choice(TEMPERATURE_MODELS),
        "radiation_cutoff_threshold": random.choice(RADIATION_CUTOFF_THRESHOLD),
        "efficiency": effieciency,
        "angle_output_units": random.choice(ANGLE_OUTPUT_UNITS),
        "statistics": random.choice(BOOLEAN_CHOICES),
        "groupby": random.choice(GROUPBY),
        "csv": random.choice(CSV_CHOICES),
        "verbose": random.randint(*VERBOSE_RANGE),
        "quiet": random.choice(BOOLEAN_CHOICES),
        "fingerprint": random.choice(BOOLEAN_CHOICES),
        "quick_response_code": random.choice([code.value for code in QuickResponseCode]),
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
        "/power/broadband",
        params=parameters,
    )
    print(f"{response.text=}")
    assert response.status_code == expected_status_code
    print("-----------------------")