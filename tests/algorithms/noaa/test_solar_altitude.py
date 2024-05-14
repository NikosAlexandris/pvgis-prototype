import pytest

from pvgisprototype.algorithms.noaa.solar_altitude import calculate_solar_altitude_time_series_noaa

from .cases.solar_altitude import cases_solar_altitude_noaa
from .cases.solar_altitude import cases_solar_altitude_noaa_ids
from ..conftest import GenericCheckCustomObjects


class TestSolarAltitudeNOAA(GenericCheckCustomObjects):

    @pytest.fixture(params=cases_solar_altitude_noaa, ids=cases_solar_altitude_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def operation(self):
        return calculate_solar_altitude_time_series_noaa