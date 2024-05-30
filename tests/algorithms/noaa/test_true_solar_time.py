import pytest
from pvgisprototype.algorithms.noaa.solar_time import calculate_true_solar_time_time_series_noaa

from .cases.true_solar_time import cases_true_solar_time_noaa
from .cases.true_solar_time import cases_true_solar_time_ids

from ..conftest import GenericCheckCustomObjects


class TestCalculateTrueSolarTimeNOAA(GenericCheckCustomObjects):

    @pytest.fixture(params=cases_true_solar_time_noaa, ids=cases_true_solar_time_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def operation(self):
        return calculate_true_solar_time_time_series_noaa