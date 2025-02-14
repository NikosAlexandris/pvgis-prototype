import pytest
from pandas import Timedelta
from numpy import abs
from pvgisprototype.algorithms.noaa.event_time import calculate_event_time_series_noaa

from .cases.event_time import cases_event_time_noaa 
from .cases.event_time import cases_event_time_noaa_ids
from ..conftest import ValidateDataModel

class TestEventTimeNOAA(ValidateDataModel):

    @pytest.fixture(params=cases_event_time_noaa, ids=cases_event_time_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_event_time_series_noaa

    def test_value(self, calculated, expected, tolerance:Timedelta=Timedelta(seconds=5)):
        difference = abs(calculated.value - expected.value)
        accepted = difference <= tolerance
        assert accepted.all()

    def test_event(self, calculated, expected):
        assert calculated.event == expected.event

    def test_unit(self, calculated, expected):
        pytest.skip()
    
    def test_dtype(self, calculated, expected):
        pytest.skip()

    def test_shape(self, calculated, expected):
        pytest.skip()
