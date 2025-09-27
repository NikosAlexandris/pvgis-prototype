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

from pvgisprototype.algorithms.iqbal.solar_incidence import calculate_solar_incidence_series_iqbal

from .cases.solar_incidence import cases_solar_incidence_iqbal
from .cases.solar_incidence import cases_solar_incidence_iqbal_ids
from .cases.solar_incidence import cases_solar_incidence_iqbal_pvlib
from .cases.solar_incidence import cases_solar_incidence_iqbal_pvlib_ids
from ..conftest import ValidateDataModel

class TestSolarIncidenceIQBAL(ValidateDataModel):

    @pytest.fixture(params=cases_solar_incidence_iqbal, ids=cases_solar_incidence_iqbal_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_solar_incidence_series_iqbal
    
    @pytest.fixture(params=cases_solar_incidence_iqbal_pvlib, ids=cases_solar_incidence_iqbal_pvlib_ids)
    def cases_pvlib(self, request):
        return request.param

    @pytest.fixture
    def calculated_pvlib_(self, function, cases_pvlib):
        return function(**cases_pvlib[0])
    
    @pytest.fixture
    def expected_pvlib(self, cases_pvlib):
        return cases_pvlib[1]
    
    def test_iqbal_pvlib(self, calculated_pvlib_, expected_pvlib, tolerance:float=1):
        assert isclose(calculated_pvlib_.degrees, expected_pvlib, atol = tolerance).all()
