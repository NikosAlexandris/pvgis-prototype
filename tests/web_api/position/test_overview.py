import pytest

from ..conftest import ValidateWebAPI
from ...generators.web_api.generate_cases_position_overview import generate_cases_solar_position_overview

class TestSolarPositionOverview(ValidateWebAPI):
    
    @pytest.fixture(autouse=True)
    def endpoint(self):
        self.endpoint="/solar-position/overview"
    
    @pytest.fixture(params=generate_cases_solar_position_overview())
    def cases(self, request):
        return request.param