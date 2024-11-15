import pytest

from pvgisprototype.api.surface.optimize_angles import optimize_angles

from .cases.cases_optimizer_tilt import cases, cases_ids
from .conftest import ValidateOptimiser


class TestOptimizerTilt(ValidateOptimiser):

    @pytest.fixture(params=cases, ids=cases_ids)
    def cases(self, request):
        yield request.param

    @pytest.fixture
    def function(self):
        yield optimize_angles
