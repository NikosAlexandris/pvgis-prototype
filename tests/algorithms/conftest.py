import pytest
from numpy import isclose

TOLERANCE_LEVELS = [1, 1e-1, 1e-2]


class ValidateDataModel:
    """A test class for native PVGIS data models

    This class provides a set of static methods and pytest fixtures
    to validate the structure and attributes of native PVGIS data models.
    It is designed to check the consistency between an actual object (`in_`)
    and an expected object (`expected`) by comparing their `type`, `value`,
    `unit`, data type (`dtype`), and `shape`.

    PVGIS' data models are generated dynamically based on Pydantic's BaseModel.
    A generic layout for PVGIS' native data models comprises the following
    fields, as per Pydantic's terminology :

    - value
    - unit
    - symbol
    - description

    and then other object-specific fields such as for example :

        - min_radians
        - max_radians

        for angular measurements 

    See Also
    --------
    calculated: Input parameters
    expected: The expected output
    tolerance: Refers to NumPy's `isclose() function where `atol` (float) is
    the absolute tolerance parameter (see Notes). See also `numpy.isclose()`.
    function: The function 

    Notes
    -----
    This class draws inspiration from the Pyxu project [0]_.

    References
    ----------
    .. [0] @software{pyxu-framework,
      author       = {Matthieu Simeoni and
                      Sepand Kashani and
                      Joan Rué-Queralt and
                      Pyxu Developers},
      title        = {pyxu-org/pyxu: pyxu},
      publisher    = {Zenodo},
      doi          = {10.5281/zenodo.4486431},
      url          = {https://doi.org/10.5281/zenodo.4486431}
    }

    Examples
    --------

    Methods
    -------
    _check_type(calculated, expected):
        Assert that the types of the input and expected objects are the same.

    _check_value(calculated, expected, tolerance: float):
        Assert that the values of the input and expected objects are close within a given tolerance level.

    _check_unit(calculated, expected):
        Assert that the units of the input and expected objects are identical.

    _check_dtype(calculated, expected):
        Assert that the data types of the input and expected object values are the same.

    _check_shape(calculated, expected):
        Assert that the shapes of the input and expected object values match.

    Fixtures
    --------
    calculated(function, cases):
        Returns an actual object created from an function and the first case from the provided test cases.

    expected(cases):
        Returns the expected object based on the second case in the provided test cases.

    Test Methods
    -------------
    test_type(calculated, expected):
        Tests that the input and expected objects are of the same type.

    test_value(calculated, expected, tolerance: float):
        Tests that the input and expected object values are close within the specified tolerance.

    test_unit(calculated, expected):
        Tests that the units of the input and expected objects match.

    test_dtype(calculated, expected):
        Tests that the data types of the input and expected object values match.

    test_shape(calculated, expected):
        Tests that the shapes of the input and expected object values are identical.
    """

    @staticmethod
    def _check_type(calculated, expected):
        assert type(calculated) == type(expected)
    
    @staticmethod
    def _check_value(calculated, expected, tolerance:float):
        assert isclose(calculated.value, expected.value, atol = tolerance).all()

    @staticmethod
    def _check_unit(calculated, expected):
        assert calculated.unit == expected.unit

    @staticmethod
    def _check_dtype(calculated, expected):
        assert calculated.value.dtype == expected.value.dtype

    @staticmethod
    def _check_shape(calculated, expected):
        assert calculated.value.shape == expected.value.shape

    @pytest.fixture
    def calculated(self, function, cases):
        return function(**cases[0])
    
    @pytest.fixture
    def expected(self, cases):
        return cases[1]
    
    def test_type(self, calculated, expected):
        self._check_type(calculated, expected)

    @pytest.mark.parametrize('tolerance', TOLERANCE_LEVELS)
    def test_value(self, calculated, expected, tolerance:float):
        self._check_value(calculated, expected, tolerance=tolerance)
    
    def test_unit(self, calculated, expected,):
        self._check_unit(calculated, expected)
    
    def test_dtype(self, calculated, expected,):
        self._check_dtype(calculated, expected)

    def test_shape(self, calculated, expected):
        self._check_shape(calculated, expected)
