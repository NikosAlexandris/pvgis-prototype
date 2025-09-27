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
import math

import pytest

from pvgisprototype.api.surface.optimize_angles import optimize_angles

from .cases.cases_optimizer_tilt_and_orientation import cases, cases_ids
from .conftest import ValidateOptimiser

TOLERANCE_LEVELS = [
    math.radians(1),
    math.radians(10),
    math.radians(20),
    math.radians(40),
]


class TestOptimizer(ValidateOptimiser):

    @pytest.fixture(params=cases, ids=cases_ids)
    def cases(self, request):
        yield request.param

    @pytest.fixture
    def function(self):
        yield optimize_angles

    @pytest.mark.parametrize("tolerance", TOLERANCE_LEVELS)
    def test_value(self, calculated, expected, tolerance: float):
        ValidateOptimiser._check_value(calculated, expected, tolerance=tolerance)
