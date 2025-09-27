#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
import random
from datetime import datetime

from pvgisprototype.api.position.models import (
    ShadingModel,
    SolarIncidenceModel,
    SolarPositionModel,
    SolarTimeModel,
)
from pvgisprototype.web_api.schemas import AngleOutputUnit, Timezone

from .utilities import generate_random_date_pair, validate_time

random.seed(22227)
NUMBER_OF_TESTS = 20000


def generate_cases_solar_position_overview(number_of_tests=NUMBER_OF_TESTS):
    """Generate random combinations of parameters."""

    NOT_IMPLEMENTED_MODELS = {
        "position": [
            SolarPositionModel.hofierka,
            SolarPositionModel.pvlib,
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

    date_range_start = datetime(2005, 1, 1)
    date_range_end = datetime(2020, 12, 31)
    timezones = [timezone.value for timezone in Timezone]

    for _ in range(number_of_tests):

        # Generate random values for the parameters
        start_date, end_date = generate_random_date_pair(
            date_range_start, date_range_end
        )
        timezone = random.choice(timezones)

        if not validate_time(start_date, timezone) or not validate_time(
            end_date, timezone
        ):
            expected_status_code = 400

        longitude = random.uniform(8.5, 8.7)
        latitude = random.uniform(45.7, 45.9)
        elevation = random.randint(200, 250)
        surface_orientation = random.uniform(0, 360)
        surface_tilt = random.uniform(0, 180)
        apply_atmospheric_refraction = random.choice([True, False])
        position_model = random.choice(
            [
                {
                    "model": model.value,
                    "expected_status_code": (
                        400 if model in NOT_IMPLEMENTED_MODELS["position"] else 200
                    ),
                }
                for model in SolarPositionModel
            ]
        )
        incidence_model = random.choice(
            [
                {
                    "model": model.value,
                    "expected_status_code": (
                        400 if model in NOT_IMPLEMENTED_MODELS["incidence"] else 200
                    ),
                }
                for model in SolarIncidenceModel
            ]
        )
        horizon_profile = random.choice(
            ["PVGIS", "80,80,80,80", "0,0,0,0", "10,20,30,40"]
        )
        shading_model = random.choice(
            [
                {
                    "model": model.value,
                    "expected_status_code": (
                        400 if model in NOT_IMPLEMENTED_MODELS["shading"] else 200
                    ),
                }
                for model in ShadingModel
            ]
        )
        zero_negative_solar_incidence_angle = random.choice([True, False])
        solar_time_model = random.choice([model.value for model in SolarTimeModel])
        angle_output_units = random.choice([unit.value for unit in AngleOutputUnit])
        csv = random.choice(["ΑΛΕΞΑΝΔΡΟΣ", None, "test"])
        verbose = random.randint(0, 9)
        fingerprint = random.choice([True, False])

        # Determine the expected status code
        expected_status_code = (
            400
            if (
                position_model["expected_status_code"] == 400
                or incidence_model["expected_status_code"] == 400
                or shading_model["expected_status_code"] == 400
            )
            else 200
        )

        yield (
            {
                "longitude": longitude,
                "latitude": latitude,
                "elevation": elevation,
                "surface_orientation": surface_orientation,
                "surface_tilt": surface_tilt,
                "start_time": start_date,
                "end_time": end_date,
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
            },
            expected_status_code,
        )
