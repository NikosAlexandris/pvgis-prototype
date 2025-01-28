import pytest

from ..conftest import ValidateWebAPI
from ...generators.web_api.generate_cases_power_broadband import generate_cases_power_broadband

class TestPowerBroadband(ValidateWebAPI):
    
    @pytest.fixture(autouse=True)
    def endpoint(self):
        self.endpoint="/power/broadband"
    
    @pytest.fixture(params=generate_cases_power_broadband())
    def cases(self, request):
        return request.param