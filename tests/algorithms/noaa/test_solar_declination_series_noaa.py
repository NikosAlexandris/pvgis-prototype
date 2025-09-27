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

from pvgisprototype.algorithms.noaa.solar_declination import calculate_solar_declination_series_noaa

from .cases.solar_declination_angle_noaa import cases_solar_declination_angle_noaa
from .cases.solar_declination_angle_noaa import cases_solar_declination_angle_noaa_ids
from ..conftest import ValidateDataModel


class TestSolarDeclinationNOAA(ValidateDataModel):

    @pytest.fixture(params=cases_solar_declination_angle_noaa, ids=cases_solar_declination_angle_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_solar_declination_series_noaa
