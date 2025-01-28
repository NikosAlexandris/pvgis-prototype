import pytest

from ..conftest import ValidateWebAPI
from ...generators.web_api.generate_cases_power_broadband_multiple_surfaces import generate_cases_power_broadband_multiple_surfaces

class TestPowerBroadbandMultipleSurfaces(ValidateWebAPI):
    
    @pytest.fixture(autouse=True)
    def endpoint(self):
        self.endpoint="/power/broadband-multiple-surfaces"
    
    @pytest.fixture(params=generate_cases_power_broadband_multiple_surfaces())
    def cases(self, request):
        return request.param