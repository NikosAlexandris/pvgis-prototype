from datetime import datetime
from typing import Union
from numpy import isclose

import pytest
from pandas import Timestamp

from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_time_series_noaa
from pvgisprototype import SolarDeclination

from .cases.solar_declination_angle_noaa import cases_solar_declination_angle_noaa
from .cases.solar_declination_angle_noaa import cases_solar_declination_angle_noaa_ids
from .conftest import GenericCheckCustomObjects


class TestSolarDeclinationNOAA(GenericCheckCustomObjects):

    @pytest.fixture(params=cases_solar_declination_angle_noaa, ids=cases_solar_declination_angle_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def operation(self):
        return calculate_solar_declination_time_series_noaa
