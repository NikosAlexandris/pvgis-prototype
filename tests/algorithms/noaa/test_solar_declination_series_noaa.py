import pytest

from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_series_noaa

from .cases.solar_declination_angle_noaa import cases_solar_declination_angle_noaa
from .cases.solar_declination_angle_noaa import cases_solar_declination_angle_noaa_ids
from ..conftest import ValidateDataModel


class TestSolarDeclinationNOAA(ValidateDataModel):

    @pytest.fixture(params=cases_solar_declination_angle_noaa, ids=cases_solar_declination_angle_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_solar_declination_series_noaa
