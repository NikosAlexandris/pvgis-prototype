
import pytest
from pvgisprototype.algorithms.noaa.equation_of_time import calculate_equation_of_time_series_noaa

from .cases.equation_of_time_noaa import cases_equation_of_time_noaa 
from .cases.equation_of_time_noaa import cases_equation_of_time_noaa_ids
from .cases.equation_of_time_noaa import cases_equation_of_time_noaa_invalid
from ..conftest import ValidateDataModel


class TestCalculateEquationOfTimeNOAA(ValidateDataModel):

    @pytest.fixture(params=cases_equation_of_time_noaa, ids=cases_equation_of_time_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_equation_of_time_series_noaa
    
    @pytest.fixture(params=cases_equation_of_time_noaa_invalid)
    def calculated_invalid(self, request):
        return request.param
    
    def test_invalid_input_datetime_string(self, calculated_invalid, function):
        with pytest.raises(calculated_invalid[1]):  
            _ = function(**calculated_invalid[0])