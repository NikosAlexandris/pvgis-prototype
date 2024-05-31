import pytest
from numpy import isclose
from numpy import mod
from numpy import where
from numpy import abs

from pvgisprototype.algorithms.noaa.solar_azimuth import calculate_solar_azimuth_series_noaa

from .cases.solar_azimuth import cases_solar_azimuth_noaa
from .cases.solar_azimuth import cases_solar_azimuth_noaa_ids
from .cases.solar_azimuth import cases_solar_azimuth_noaa_usno
from .cases.solar_azimuth import cases_solar_azimuth_noaa_usno_ids
from .cases.solar_azimuth import cases_solar_azimuth_noaa_pvlib
from .cases.solar_azimuth import cases_solar_azimuth_noaa_pvlib_ids
from ..conftest import GenericCheckCustomObjects


class TestSolarAzimuthNOAA(GenericCheckCustomObjects):

    @pytest.fixture(params=cases_solar_azimuth_noaa, ids=cases_solar_azimuth_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def operation(self):
        return calculate_solar_azimuth_series_noaa
    
    def test_value(self, in_, expected, tolerance:float=0.01): # FIXME NEEDS TOLERANCE FOR HANDLING EXTREME CASES
        self._check_value(in_, expected, tolerance=tolerance)
    
    def test_extra_object_attributes(self, in_):
        assert in_.position_algorithm == "NOAA"
        assert in_.timing_algorithm == "NOAA"

    @pytest.fixture(params=cases_solar_azimuth_noaa_usno, ids=cases_solar_azimuth_noaa_usno_ids)
    def cases_usno(self, request):
        return request.param

    @pytest.fixture
    def calculated_usno_(self, operation, cases_usno):
        return operation(**cases_usno[0])
    
    @pytest.fixture
    def expected_usno(self, cases_usno):
        return cases_usno[1]
    
    @pytest.mark.parametrize("tolerance", [8]) # degrees
    def test_azimuth_usno(self, calculated_usno_, expected_usno, tolerance):
        assert isclose(calculated_usno_.degrees, expected_usno, atol = tolerance).all()
    
    @pytest.fixture(params=cases_solar_azimuth_noaa_pvlib, ids=cases_solar_azimuth_noaa_pvlib_ids)
    def cases_pvlib(self, request):
        return request.param

    @pytest.fixture
    def calculated_pvlib_(self, operation, cases_pvlib):
        return operation(**cases_pvlib[0])
    
    @pytest.fixture
    def expected_pvlib(self, cases_pvlib):
        return cases_pvlib[1]
    
    @pytest.mark.parametrize("tolerance", [10]) # degrees
    def test_azimuth_pvlib(self, calculated_pvlib_, expected_pvlib, tolerance):
        calculated_mod = mod(calculated_pvlib_.degrees, 360)
        expected_mod = mod(expected_pvlib, 360)    
        differences = abs(calculated_mod - expected_mod)
        differences = where(differences > 180, 360 - differences, differences)
    
        assert isclose(differences, 0, atol=tolerance).all()
