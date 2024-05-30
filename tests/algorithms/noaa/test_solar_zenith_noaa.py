import pytest

from pvgisprototype.algorithms.noaa.solar_zenith import calculate_solar_zenith_time_series_noaa

from .cases.solar_zenith import cases_solar_zenith
from .cases.solar_zenith import cases_solar_zenith_ids
from ..conftest import GenericCheckCustomObjects

class TestSolarZenithNOAA(GenericCheckCustomObjects):

    @pytest.fixture(params=cases_solar_zenith, ids=cases_solar_zenith_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def operation(self):
        return calculate_solar_zenith_time_series_noaa