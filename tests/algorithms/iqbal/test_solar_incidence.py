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
