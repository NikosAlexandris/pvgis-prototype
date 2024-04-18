import pytest
from numpy import isclose

class GenericCheckCustomObjects:
    """Check structure of Pydantic custom objects.
    """

    @staticmethod
    def _check_type(in_, expected):
        assert type(in_) == type(expected)
    
    @staticmethod
    def _check_value(in_, expected, rtol:float):
        assert isclose(in_.value, expected.value, rtol).all()

    @staticmethod
    def _check_unit(in_, expected):
        assert in_.unit == expected.unit

    @staticmethod
    def _check_dtype(in_, expected):
        assert in_.value.dtype == expected.value.dtype

    @staticmethod
    def _check_shape(in_, expected):
        assert in_.value.shape == expected.value.shape

    def test_type(self, in_, expected):
        self._check_type(in_, expected)

    def test_value(self, in_, expected, rtol:float=1e-2):
        self._check_value(in_, expected, rtol=rtol)
    
    def test_unit(self, in_, expected,):
        self._check_unit(in_, expected)
    
    def test_dtype(self, in_, expected,):
        self._check_dtype(in_, expected)

    def test_shape(self, in_, expected):
        self._check_shape(in_, expected)
