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
from pandas import Timedelta
from numpy import abs
from pvgisprototype.algorithms.noaa.event_time import calculate_event_time_series_noaa

from .cases.event_time import cases_event_time_noaa 
from .cases.event_time import cases_event_time_noaa_ids
from ..conftest import ValidateDataModel

class TestEventTimeNOAA(ValidateDataModel):

    @pytest.fixture(params=cases_event_time_noaa, ids=cases_event_time_noaa_ids)
    def cases(self, request):
        return request.param

    @pytest.fixture
    def function(self):
        return calculate_event_time_series_noaa

    def test_value(self, calculated, expected, tolerance:Timedelta=Timedelta(seconds=5)):
        difference = abs(calculated.value - expected.value)
        accepted = difference <= tolerance
        assert accepted.all()

    def test_event(self, calculated, expected):
        assert calculated.event == expected.event

    def test_unit(self, calculated, expected):
        pytest.skip()
    
    def test_dtype(self, calculated, expected):
        pytest.skip()

    def test_shape(self, calculated, expected):
        pytest.skip()
