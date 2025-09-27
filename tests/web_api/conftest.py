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
from fastapi.testclient import TestClient
from pvgisprototype.webapi import app


class ValidateWebAPI:

    @pytest.fixture(autouse=True)
    def client(self):
        self.client = TestClient(app)

    def _call(self, cases):
        return self.client.get(
            self.endpoint,
            params=cases[0],
        )

    @pytest.fixture
    def response(self, cases):
        return self._call(cases)
    
    @pytest.fixture
    def expected(self, cases):
        return cases[1]

    @staticmethod
    def _check_equality(calculated, expected):
        assert calculated == expected

    def test_response_status(self, response, expected):
        self._check_equality(response.status_code, expected)