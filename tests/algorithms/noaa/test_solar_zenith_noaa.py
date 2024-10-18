import pytest

from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_series_noaa

from .cases.solar_zenith import cases_solar_zenith
from .cases.solar_zenith import cases_solar_zenith_ids
from ..conftest import ValidateDataModel

class TestSolarZenithNOAA(ValidateDataModel):

    @pytest.fixture(params=cases_solar_zenith, ids=cases_solar_zenith_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_solar_zenith_series_noaa