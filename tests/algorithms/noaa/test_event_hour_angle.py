import pytest
from pvgisprototype.algorithms.noaa.event_hour_angle import calculate_event_hour_angle_series_noaa

from .cases.event_hour_angle import cases_event_hour_angle_noaa
from .cases.event_hour_angle import cases_event_hour_angle_noaa_ids
from ..conftest import ValidateDataModel

class TestEventHourAngleNOAA(ValidateDataModel):

    @pytest.fixture(params=cases_event_hour_angle_noaa, ids=cases_event_hour_angle_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_event_hour_angle_series_noaa