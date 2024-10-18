import pytest
from pvgisprototype.algorithms.noaa.time_offset import calculate_time_offset_series_noaa

from .cases.time_offset_noaa import cases_time_offset_noaa
from .cases.time_offset_noaa import cases_time_offset_noaa_ids

from ..conftest import ValidateDataModel


class TestCalculateTimeOffsetNOAA(ValidateDataModel):

    @pytest.fixture(params=cases_time_offset_noaa, ids=cases_time_offset_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_time_offset_series_noaa