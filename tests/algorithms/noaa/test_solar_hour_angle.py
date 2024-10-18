import pytest

from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_series_noaa

from .cases.solar_hour_angle import cases_solar_hour_angle_noaa
from .cases.solar_hour_angle import cases_solar_hour_angle_ids
from ..conftest import ValidateDataModel

class TestSolarHourAngleNOAA(ValidateDataModel):

    @pytest.fixture(params=cases_solar_hour_angle_noaa, ids=cases_solar_hour_angle_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_solar_hour_angle_series_noaa