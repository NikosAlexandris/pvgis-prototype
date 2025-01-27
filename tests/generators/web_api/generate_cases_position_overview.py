import random
from datetime import datetime, timedelta

from pvgisprototype.web_api.schemas import Timezone, AngleOutputUnit
from pvgisprototype.api.position.models import (
    SolarPositionModel, 
    SolarIncidenceModel, 
    ShadingModel, 
    SolarTimeModel
)

random.seed(22227)
NUMBER_OF_TESTS = 20000
DATE_RANGE = {"start": datetime(2005, 1, 1), "end": datetime(2020, 12, 31)}

NOT_IMPLEMENTED_MODELS = {
    "position": [
        SolarPositionModel.hofierka,
        SolarPositionModel.pvlib,
        SolarPositionModel.pysolar,
        SolarPositionModel.skyfield,
        SolarPositionModel.suncalc,
        SolarPositionModel.all,
    ],
    "incidence": [
        SolarIncidenceModel.pvis,
        SolarIncidenceModel.all,
    ],
    "shading": [
        ShadingModel.all,
        ShadingModel.pvlib,
    ],
}


# Utility functions
def generate_random_date_pair(start=DATE_RANGE["start"], end=DATE_RANGE["end"]):
    """Generate a random start_date and end_date such that start_date < end_date."""
    start_date = start + timedelta(days=random.randint(0, (end - start).days))
    end_date = start_date + timedelta(days=random.randint(1, (end - start_date).days))
    return start_date, end_date


def generate_cases_solar_position_overview(number_of_tests = NUMBER_OF_TESTS):
    """Generate random combinations of parameters."""
    for _ in range(number_of_tests):
        longitude = random.uniform(8.5, 8.7)
        latitude = random.uniform(45.7, 45.9)
        elevation = random.randint(200, 250)
        surface_orientation = random.uniform(0, 360)
        surface_tilt = random.uniform(0, 180)
        start_date, end_date = generate_random_date_pair()
        timezone = random.choice(list(Timezone)).value
        apply_atmospheric_refraction = random.choice([True, False])
        position_model = random.choice(
            [{"model": model.value, "expected_status_code": 400 if model in NOT_IMPLEMENTED_MODELS["position"] else 200}
             for model in SolarPositionModel]
        )
        incidence_model = random.choice(
            [{"model": model.value, "expected_status_code": 400 if model in NOT_IMPLEMENTED_MODELS["incidence"] else 200}
             for model in SolarIncidenceModel]
        )
        horizon_profile = random.choice(["PVGIS", "80,80,80,80", "0,0,0,0", "10,20,30,40"])
        shading_model = random.choice(
            [{"model": model.value, "expected_status_code": 400 if model in NOT_IMPLEMENTED_MODELS["shading"] else 200}
             for model in ShadingModel]
        )
        zero_negative_solar_incidence_angle = random.choice([True, False])
        solar_time_model = random.choice([model.value for model in SolarTimeModel])
        angle_output_units = random.choice([unit.value for unit in AngleOutputUnit])
        csv = random.choice(["ΑΛΕΞΑΝΔΡΟΣ", None, "test"])
        verbose = random.randint(0, 9)
        fingerprint = random.choice([True, False])

        # Determine the expected status code
        expected_status_code = (
            400 if (position_model["expected_status_code"] == 400 or
                    incidence_model["expected_status_code"] == 400 or
                    shading_model["expected_status_code"] == 400)
            else 200
        )

        yield ({
            "longitude": longitude,
            "latitude": latitude,
            "elevation": elevation,
            "surface_orientation": surface_orientation,
            "surface_tilt": surface_tilt,
            "start_time": start_date.strftime("%Y-%m-%d"),
            "end_time": end_date.strftime("%Y-%m-%d"),
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
        }, expected_status_code)
