import pytest

from pvgisprototype.algorithms.noaa.solar_hour_angle import calculate_solar_hour_angle_time_series_noaa

from .cases.solar_hour_angle import cases_solar_hour_angle_noaa
from .cases.solar_hour_angle import cases_solar_hour_angle_ids
from .conftest import GenericCheckCustomObjects

class TestSolarHourAngleNOAA(GenericCheckCustomObjects):

    @pytest.fixture(params=cases_solar_hour_angle_noaa, ids=cases_solar_hour_angle_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def operation(self):
        return calculate_solar_hour_angle_time_series_noaa