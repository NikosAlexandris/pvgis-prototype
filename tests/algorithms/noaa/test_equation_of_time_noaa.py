
import pytest
from pvgisprototype.algorithms.noaa.equation_of_time import calculate_equation_of_time_series_noaa

from .cases.equation_of_time_noaa import cases_equation_of_time_noaa 
from .cases.equation_of_time_noaa import cases_equation_of_time_noaa_ids
from .cases.equation_of_time_noaa import cases_equation_of_time_noaa_invalid
from ..conftest import GenericCheckCustomObjects


class TestCalculateEquationOfTimeNOAA(GenericCheckCustomObjects):

    @pytest.fixture(params=cases_equation_of_time_noaa, ids=cases_equation_of_time_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def operation(self):
        return calculate_equation_of_time_series_noaa
    
    @pytest.fixture(params=cases_equation_of_time_noaa_invalid)
    def in_invalid(self, request):
        return request.param
    
    def test_invalid_input_datetime_string(self, in_invalid, operation):
        with pytest.raises(in_invalid[1]):  
            _ = operation(**in_invalid[0])