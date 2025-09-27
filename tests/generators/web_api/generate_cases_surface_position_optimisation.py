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

from pvgisprototype.api.position.models import ShadingModel
from pvgisprototype.algorithms.huld.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerModeWithoutNone,
)
from pvgisprototype.web_api.schemas import AngleOutputUnit, Timezone

from .utilities import generate_random_date_pair, remove_none_values, validate_time

random.seed(22227)
NUMBER_OF_TESTS = 20000


def generate_cases_surface_position_optimisation(number_of_tests=NUMBER_OF_TESTS):
    """Generate random test cases for power broadband calculations."""
    # Define the ranges and choices for random sampling
    longitude = [8.628]
    latitude = [45.812]
    elevation_range = (200, 250)
    surface_orientation_range = (0, 360)
    surface_tilt_range = (0, 180)
    date_range_start = datetime(2005, 1, 1)
    date_range_end = datetime(2020, 12, 31)
    timezones = [timezone.value for timezone in Timezone]
    linke_turbidity_range = (0, 8)
    horizon_profile_choices = ["PVGIS", "80,80,80,80", "0,0,0,0", "10,20,30,40"]
    shading_models = [shading_model for shading_model in ShadingModel]
    not_implemented_shading_models = [ShadingModel.all, ShadingModel.pvlib]
    photovoltaic_module_models = [module.value for module in PhotovoltaicModuleModel]
    angle_output_units = [unit.value for unit in AngleOutputUnit]
    verbose_range = (0, 9)
    optimize_surface_position = [
        optimise_surface_position.value
        for optimise_surface_position in SurfacePositionOptimizerModeWithoutNone
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

        parameters = remove_none_values(
            {
                "longitude": random.choice(longitude),
                "latitude": random.choice(latitude),
                "elevation": random.randint(*elevation_range),
                "surface_orientation": random.uniform(*surface_orientation_range),
                "surface_tilt": random.uniform(*surface_tilt_range),
                "start_time": start_date,
                "end_time": end_date,
                "timezone": timezone,
                "linke_turbidity_factor_series": random.uniform(*linke_turbidity_range),
                "horizon_profile": random.choice(horizon_profile_choices),
                "shading_model": shading_model.value,
                "photovoltaic_module": random.choice(photovoltaic_module_models),
                "angle_output_units": random.choice(angle_output_units),
                "verbose": random.randint(*verbose_range),
                "optimise_surface_position": random.choice(optimize_surface_position),
                "sampling_method_shgo": random.choice(sampling_method),
            }
        )

        yield parameters, expected_status_code
