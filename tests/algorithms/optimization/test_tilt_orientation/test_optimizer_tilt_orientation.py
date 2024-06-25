import pytest
import math
from tests.algorithms.optimization.test_tilt_orientation.cases_optimizer_tilt_orientation import cases
from pvgisprototype.api.surface.optimize_angles import optimize_angles

class TestOptimizer():

    #'create' each case
    @pytest.fixture(params=cases)
    def cases(self, request):
        return request.param

    #open the function I want to run
    @pytest.fixture
    def operation(self):
        return optimize_angles
    
    @staticmethod
    def _check_type(in_, expected):
        assert type(in_) == type(expected)
    
    @staticmethod
    def _check_value(in_, expected, tolerance:float):
        #assert abs(in_['surface_orientation'].value - expected['surface_orientation'].value) <= tolerance
        #assert abs(in_['surface_tilt'].value - expected['surface_tilt'].value) <= tolerance
        assert abs(in_['mean_power_output'] - expected['mean_power_output']) <= float(1)

    @staticmethod
    def _check_unit(in_, expected):
        assert in_['surface_orientation'].unit == expected['surface_orientation'].unit
        assert in_['surface_tilt'].unit == expected['surface_tilt'].unit


    @staticmethod
    def _check_dtype(in_, expected):
        assert isinstance(in_['surface_orientation'].value, type(expected['surface_orientation'].value))
        assert isinstance(in_['surface_tilt'].value, type(expected['surface_tilt'].value))
        #assert isinstance(in_['mean_power_output'], type(expected['mean_power_output']))

    @pytest.fixture
    def in_(self, operation, cases):
        return operation(**cases[0])
    
    @pytest.fixture
    def expected(self, cases):
        return cases[1]
    
    def test_type(self, in_, expected):
        self._check_type(in_, expected)

    def test_value(self, in_, expected, tolerance:float=math.radians(1)):
        self._check_value(in_, expected, tolerance=tolerance)
    
    def test_unit(self, in_, expected,):
        self._check_unit(in_, expected)
    
    def test_dtype(self, in_, expected,):
        self._check_dtype(in_, expected)
