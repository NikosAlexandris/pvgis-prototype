import pytest

from pvgisprototype.algorithms.noaa.solar_altitude import calculate_solar_altitude_series_noaa

from .cases.solar_altitude import cases_solar_altitude_noaa
from .cases.solar_altitude import cases_solar_altitude_noaa_ids
from ..conftest import ValidateDataModel


class TestSolarAltitudeNOAA(ValidateDataModel):

    @pytest.fixture(params=cases_solar_altitude_noaa, ids=cases_solar_altitude_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_solar_altitude_series_noaa