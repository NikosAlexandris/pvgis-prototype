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