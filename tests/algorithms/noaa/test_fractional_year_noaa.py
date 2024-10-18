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
