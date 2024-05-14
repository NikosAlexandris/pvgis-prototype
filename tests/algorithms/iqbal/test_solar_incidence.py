import pytest

from pvgisprototype.algorithms.iqbal.solar_incidence import calculate_solar_incidence_time_series_iqbal

from .cases.solar_incidence import cases_solar_incidence_iqbal
from .cases.solar_incidence import cases_solar_incidence_iqbal_ids
from ..conftest import GenericCheckCustomObjects

class TestSolarIncidenceIQBAL(GenericCheckCustomObjects):

    @pytest.fixture(params=cases_solar_incidence_iqbal, ids=cases_solar_incidence_iqbal_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def operation(self):
        return calculate_solar_incidence_time_series_iqbal