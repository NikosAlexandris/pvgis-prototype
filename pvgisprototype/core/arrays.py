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
import collections.abc as cabc
import enum
import importlib.util
import types

import numpy

from pvgisprototype.constants import DATA_TYPE_DEFAULT

CUPY_ENABLED = importlib.util.find_spec("cupy") is not None
if CUPY_ENABLED:
    try:
        import cupy
    except ImportError:
        CUPY_ENABLED = False


@enum.unique
class NDArrayBackend(enum.Enum):
    """
    Supported dense array backends.
    """

    NUMPY = enum.auto()
    DASK = enum.auto()
    CUPY = enum.auto()

    @classmethod
    def default(cls) -> "NDArrayBackend":
        """Return the default array backend."""
        return cls.NUMPY

    def type(self) -> type:
        """Return the array type associated with the backend."""
        if self == NDArrayBackend.NUMPY:
            return numpy.ndarray
        elif self == NDArrayBackend.DASK:
            import dask.array
            return dask.array.core.Array
        elif self == NDArrayBackend.CUPY and CUPY_ENABLED:
            return cupy.ndarray
        else:
            raise ValueError(f"No known array type for {self.name}.")

    @classmethod
    def from_object(cls, obj) -> "NDArrayBackend":
        """Determine the array backend associated with `obj`."""
        if obj is not None:
            for backend in cls:
                if isinstance(obj, backend.type()):
                    return backend
        raise ValueError(f"No known array type to match {obj}.")

    @classmethod
    def from_gpu_flag(cls, use_gpu: bool) -> "NDArrayBackend":
        """Select array backend based on whether GPU is used."""
        return cls.CUPY if use_gpu and CUPY_ENABLED else cls.NUMPY

    def module(self, linear_algebra: bool = False) -> types.ModuleType:
        """
        Return the Python module associated with an array backend.

        Parameters
        ----------
        linear_algebra: bool
            If True, return the linear algebra submodule.
        """
        if self == NDArrayBackend.NUMPY:
            module = numpy
            linalg_module = module.linalg
        elif self == NDArrayBackend.DASK:
            module = dask.array
            linalg_module = module.linalg
        elif self == NDArrayBackend.CUPY and CUPY_ENABLED:
            module = cupy
            linalg_module = module.linalg if module is not None else None
        else:
            raise ValueError(f"No known module for {self.name}.")
        return linalg_module if linear_algebra else module


class ArrayDType(enum.Enum):
    FLOAT32 = numpy.float32
    FLOAT64 = numpy.float64
    INT32 = numpy.int32
    INT64 = numpy.int64
    BOOL = numpy.bool_
    STR = numpy.str_
    OBJECT = numpy.object_
    # Add other data types as needed

    @classmethod
    def from_string(cls, dtype_str):
        """Return the corresponding dtype object from a string."""
        try:
            return cls[dtype_str.upper()].value
        except KeyError:
            raise ValueError(
                f"Invalid dtype. Supported types are: {list(cls.__members__.keys())}"
            )


def supported_array_types() -> cabc.Collection[type]:
    types = [numpy.ndarray]
    if CUPY_ENABLED:
        types.append(cupy.ndarray)
    return tuple(types)


def create_array(
    shape,
    dtype: str = DATA_TYPE_DEFAULT,
    init_method: bool | int | float | str = "zeros",
    backend: str = "numpy",
    use_gpu: bool = False,
):
    """
    Create an array with given shape, data type, initialization method, backend, and optional GPU usage.

    Parameters
    ----------
    shape : tuple
        Shape of the array.
    dtype : str, optional
        Desired data-type for the array as a string. Default is 'float32'.
    init_method : str, optional
        Method to initialize the array. Options are 'zeros', 'ones', 'empty', and 'unset'. Default is 'zeros'.
    backend : str, optional
        The array backend to use. Options are 'numpy', 'cupy', and 'dask'. Default is 'numpy'.
    use_gpu : bool, optional
        If True, use GPU-accelerated arrays (CuPy) if available, overriding the backend choice. Default is False.

    Returns
    -------
        ndarray: An array initialized as specified.

    """
    backend = backend.upper()

    # Get the actual dtype object from the string
    dtype_obj = ArrayDType.from_string(dtype)

    # Override backend if GPU is requested and CuPy is available
    if use_gpu and CUPY_ENABLED:
        array_backend = NDArrayBackend.CUPY
    # Handle backend selection
    else:
        if backend not in NDArrayBackend.__members__:
            raise ValueError(
                f"Invalid backend. Choose among {list(NDArrayBackend.__members__.keys())}."
            )
        array_backend = NDArrayBackend[backend.upper()]

    array_module = array_backend.module()

    # Select the initialization method
    if isinstance(init_method, (int, float)):  # User-requested value !
        array = array_module.full(shape, init_method, dtype=dtype_obj)
    elif isinstance(init_method, bool):
        array = array_module.full(shape, init_method, dtype=bool)
    elif init_method == "unset":
        array = array_module.full(shape, init_method, dtype='U5')
    elif init_method == "zeros":
        array = array_module.zeros(shape, dtype=dtype_obj)
    elif init_method == "ones":
        array = array_module.ones(shape, dtype=dtype_obj)
    elif init_method == "empty":
        array = array_module.empty(shape, dtype=dtype_obj)
    # elif isinstance(init_method, str):  # Handle arbitrary string initialization
    #     if dtype_obj != numpy.str_ and dtype_obj != numpy.object_:
    #         raise ValueError("String initialization requires dtype to be 'str' or 'object'.")
    #     array = array_module.full(shape, init_method, dtype=dtype_obj)
    else:
        raise ValueError(
            "Invalid initialization method. Choose from 'zeros', 'ones', 'empty', 'unset' or provide a specific numeric or boolean value."
        )

    return array
