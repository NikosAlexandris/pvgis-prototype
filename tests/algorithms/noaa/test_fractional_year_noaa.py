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
from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_series_noaa

from .cases.fractional_year_noaa import cases_fractional_year_noaa 
from .cases.fractional_year_noaa import cases_fractional_year_noaa_ids
from .cases.fractional_year_noaa import cases_fractional_year_noaa_invalid
from ..conftest import ValidateDataModel


class TestCalculateFractionalYearNOAA(ValidateDataModel):

    @pytest.fixture(params=cases_fractional_year_noaa, ids=cases_fractional_year_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_fractional_year_series_noaa
    
    @pytest.fixture(params=cases_fractional_year_noaa_invalid)
    def calculated_invalid(self, request):
        return request.param
    
    def test_invalid_input_datetime_string(self, calculated_invalid, function):
        with pytest.raises(calculated_invalid[1]):  
            _ = function(**calculated_invalid[0])
