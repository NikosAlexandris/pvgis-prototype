from datetime import datetime
from typing import Union
from numpy import isclose

import pytest
from pandas import Timestamp
from pvgisprototype.algorithms.noaa.fractional_year import calculate_fractional_year_time_series_noaa

from .cases.fractional_year_noaa import cases_fractional_year_noaa 
from .cases.fractional_year_noaa import cases_fractional_year_noaa_ids
from .cases.fractional_year_noaa import cases_fractional_year_noaa_invalid
from .conftest import GenericCheckCustomObjects


class TestCalculateFractionalYearNOAA(GenericCheckCustomObjects):

    @pytest.fixture(params=cases_fractional_year_noaa, ids=cases_fractional_year_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def in_(self, cases):
        print(calculate_fractional_year_time_series_noaa(**cases[0]))
        return calculate_fractional_year_time_series_noaa(**cases[0])
    
    @pytest.fixture
    def expected(self, cases):
        return cases[1]
    
    @pytest.fixture(params=cases_fractional_year_noaa_invalid)
    def in_invalid(self, request):
        return request.param
    
    def test_invalid_input_datetime_string(self, in_invalid):
        with pytest.raises(in_invalid[1]):  
            _ = calculate_fractional_year_time_series_noaa(**in_invalid[0])
