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
import math
import random

import pytest

TOLERANCE_LEVELS = [math.radians(1), math.radians(2), math.radians(5), math.radians(10)]


class ValidateOptimiser:
    """Generic class for testing the optimization algorithm."""

    @pytest.fixture
    def calculated(self, function, cases):
        yield function(**cases[0])

    @pytest.fixture
    def expected(self, cases):
        yield cases[1]

    @staticmethod
    def _angle_difference(calculated_angle, expected_angle):
        difference = (calculated_angle - expected_angle) % (2 * math.pi)
        return min(difference, 2 * math.pi - difference)

    @staticmethod
    def _check_type(calculated, expected):
        assert isinstance(calculated, type(expected))

    @staticmethod
    def _check_value(calculated, expected, tolerance: float):
        assert (
            ValidateOptimiser._angle_difference(
                calculated["surface_orientation"].value,
                expected["surface_orientation"].value,
            )
            <= tolerance
        )
        assert (
            ValidateOptimiser._angle_difference(
                calculated["surface_tilt"].value, expected["surface_tilt"].value
            )
            <= tolerance
        )

    @staticmethod
    def _check_unit(calculated, expected):
        assert (
            calculated["surface_orientation"].unit
            == expected["surface_orientation"].unit
        )
        assert calculated["surface_tilt"].unit == expected["surface_tilt"].unit

    @staticmethod
    def _check_dtype(calculated, expected):
        assert isinstance(
            calculated["surface_orientation"].value,
            type(expected["surface_orientation"].value),
        )
        assert isinstance(
            calculated["surface_tilt"].value, type(expected["surface_tilt"].value)
        )

    def test_type(self, calculated, expected):
        self._check_type(calculated, expected)

    @pytest.mark.parametrize("tolerance", TOLERANCE_LEVELS)
    def test_value(self, calculated, expected, tolerance: float):
        self._check_value(calculated, expected, tolerance=tolerance)

    def test_unit(
        self,
        calculated,
        expected,
    ):
        self._check_unit(calculated, expected)

    def test_dtype(
        self,
        calculated,
        expected,
    ):
        self._check_dtype(calculated, expected)
