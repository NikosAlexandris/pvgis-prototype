#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
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
from ..conftest import ValidateDataModel


class TestSolarAzimuthNOAA(ValidateDataModel):

    @pytest.fixture(params=cases_solar_azimuth_noaa, ids=cases_solar_azimuth_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_solar_azimuth_series_noaa
    
    def test_value(self, calculated, expected, tolerance:float=0.01): # FIXME NEEDS TOLERANCE FOR HANDLING EXTREME CASES
        self._check_value(calculated, expected, tolerance=tolerance)
    
    def test_extra_object_attributes(self, calculated):
        assert calculated.solar_positioning_algorithm == "NOAA"
        assert calculated.solar_timing_algorithm == "NOAA"

    @pytest.fixture(params=cases_solar_azimuth_noaa_usno, ids=cases_solar_azimuth_noaa_usno_ids)
    def cases_usno(self, request):
        return request.param

    @pytest.fixture
    def calculated_usno_(self, function, cases_usno):
        return function(**cases_usno[0])
    
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
    def calculated_pvlib_(self, function, cases_pvlib):
        return function(**cases_pvlib[0])
    
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
