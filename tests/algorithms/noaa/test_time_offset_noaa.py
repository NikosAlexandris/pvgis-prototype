import pytest
from pvgisprototype.algorithms.noaa.time_offset import calculate_time_offset_time_series_noaa

from .cases.time_offset_noaa import cases_time_offset_noaa
from .cases.time_offset_noaa import cases_time_offset_noaa_ids

from ..conftest import GenericCheckCustomObjects


class TestCalculateTimeOffsetNOAA(GenericCheckCustomObjects):

    @pytest.fixture(params=cases_time_offset_noaa, ids=cases_time_offset_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def operation(self):
        return calculate_time_offset_time_series_noaa