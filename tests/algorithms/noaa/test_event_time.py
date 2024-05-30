import pytest
from pandas import Timedelta
from numpy import abs
from pvgisprototype.algorithms.noaa.event_time import calculate_event_time_time_series_noaa

from .cases.event_time import cases_event_time_noaa 
from .cases.event_time import cases_event_time_noaa_ids
from ..conftest import GenericCheckCustomObjects

class TestEventTimeNOAA(GenericCheckCustomObjects):

    @pytest.fixture(params=cases_event_time_noaa, ids=cases_event_time_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def operation(self):
        return calculate_event_time_time_series_noaa

    def test_value(self, in_, expected, tolerance:Timedelta=Timedelta(seconds=2)):
        difference = abs(in_.value - expected.value)
        accepted = difference <= tolerance
        assert accepted.all()

    def test_event(self, in_, expected):
        assert in_.event == expected.event

    def test_unit(self, in_, expected):
        pytest.skip()
    
    def test_dtype(self, in_, expected):
        pytest.skip()

    def test_shape(self, in_, expected):
        pytest.skip()
