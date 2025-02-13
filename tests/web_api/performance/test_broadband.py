import pytest

from ..conftest import ValidateWebAPI
from ...generators.web_api.generate_cases_performance_broadband import generate_cases_solar_performance_broadband

class TestPerformanceBroadband(ValidateWebAPI):
    
    @pytest.fixture(autouse=True)
    def endpoint(self):
        self.endpoint="/performance/broadband"
    
    @pytest.fixture(params=generate_cases_solar_performance_broadband())
    def cases(self, request):
        return request.param