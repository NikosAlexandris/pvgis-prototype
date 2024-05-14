import pytest

from pvgisprototype.algorithms.noaa.solar_azimuth import calculate_solar_azimuth_time_series_noaa

from .cases.solar_azimuth import cases_solar_azimuth_noaa
from .cases.solar_azimuth import cases_solar_azimuth_noaa_ids
from ..conftest import GenericCheckCustomObjects


class TestSolarAzimuthNOAA(GenericCheckCustomObjects):

    @pytest.fixture(params=cases_solar_azimuth_noaa, ids=cases_solar_azimuth_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def operation(self):
        return calculate_solar_azimuth_time_series_noaa
    
    def test_value(self, in_, expected, tolerance:float=0.01): # FIXME NEEDS TOLERANCE FOR HANDLING EXTREME CASES
        self._check_value(in_, expected, tolerance=tolerance)
    
    def test_extra_object_attributes(self, in_):
        assert in_.position_algorithm == "NOAA"
        assert in_.timing_algorithm == "NOAA"