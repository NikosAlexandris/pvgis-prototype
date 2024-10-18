import pytest
import math
from tests.algorithms.optimization.test_orientation.cases_optimizer_orientation import cases
from pvgisprototype.api.surface.optimize_angles import optimize_angles

class TestOptimizer():

    #'create' each case
    @pytest.fixture(params=cases)
    def cases(self, request):
        return request.param

    #open the function I want to run
    @pytest.fixture
    def function(self):
        return optimize_angles
    
    @staticmethod
    def _check_type(calculated, expected):
        assert type(calculated) == type(expected)
    
    @staticmethod
    def _check_value(calculated, expected, tolerance:float):
        assert abs(calculated['surface_orientation'].value - expected['surface_orientation'].value) <= tolerance
        assert abs(calculated['surface_tilt'].value - expected['surface_tilt'].value) <= tolerance

    @staticmethod
    def _check_unit(calculated, expected):
        assert calculated['surface_orientation'].unit == expected['surface_orientation'].unit
        assert calculated['surface_tilt'].unit == expected['surface_tilt'].unit

    @staticmethod
    def _check_dtype(calculated, expected):
        assert isinstance(calculated['surface_orientation'].value, type(expected['surface_orientation'].value))
        assert isinstance(calculated['surface_tilt'].value, type(expected['surface_tilt'].value))

    @pytest.fixture
    def calculated(self, function, cases):
        return function(**cases[0])
    
    @pytest.fixture
    def expected(self, cases):
        return cases[1]
    
    def test_type(self, calculated, expected):
        self._check_type(calculated, expected)

    def test_value(self, calculated, expected, tolerance:float=math.radians(1)):
        self._check_value(calculated, expected, tolerance=tolerance)
    
    def test_unit(self, calculated, expected,):
        self._check_unit(calculated, expected)
    
    def test_dtype(self, calculated, expected,):
        self._check_dtype(calculated, expected)
