import pytest
from pvgisprototype.algorithms.noaa.solar_time import calculate_true_solar_time_series_noaa

from .cases.true_solar_time import cases_true_solar_time_noaa
from .cases.true_solar_time import cases_true_solar_time_ids

from ..conftest import ValidateDataModel


class TestCalculateTrueSolarTimeNOAA(ValidateDataModel):

    @pytest.fixture(params=cases_true_solar_time_noaa, ids=cases_true_solar_time_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_true_solar_time_series_noaa