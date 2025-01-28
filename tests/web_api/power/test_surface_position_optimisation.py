import pytest

from ..conftest import ValidateWebAPI
from ...generators.web_api.generate_cases_surface_position_optimisation import generate_cases_surface_position_optimisation

class TestSurfacePositionOptimisation(ValidateWebAPI):
    
    @pytest.fixture(autouse=True)
    def endpoint(self):
        self.endpoint="/power/surface-position-optimisation"
    
    @pytest.fixture(params=generate_cases_surface_position_optimisation())
    def cases(self, request):
        return request.param