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
