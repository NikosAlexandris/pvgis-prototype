from rich import print
import numpy as np
import dask.array as da

# Attempt to import CuPy, handle the case where it is not available
try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False

from pvgisprototype.validation.arrays import NDArrayBackend
from pvgisprototype.validation.arrays import create_array

def process_array(array):
    backend = NDArrayBackend.from_object(array)

    if backend == NDArrayBackend.NUMPY:
        print("Processing a NumPy array")
        # Example operation: Sum all elements in the array
        result = np.sum(array)
        print(f"Input type: {type(array)}, Sum: {result}")
    elif backend == NDArrayBackend.CUPY and CUPY_AVAILABLE:
        print("Processing a CuPy array")
        # Example operation: Sum all elements in the array
        result = cp.sum(array)
        print(f"Input type: {type(array)}, Sum: {result}")
    elif backend == NDArrayBackend.DASK:
        print("Processing a Dask array")
        # Example operation: Sum all elements in the array (computed)
        result = da.sum(array).compute()
        print(f"Input type: {type(array)}, Computed Sum: {result}")
    else:
        raise ValueError("Unknown array backend")

# Example use
print(f'[underline]Example[/underline]')
shape = (10, 10)
dtype = 'float64'
init_method = 'ones'
backend = 'numpy'

message = f'Create an array of :\n'
message += f'  shape [code]{shape}[/code]\n'
message += f'  method [code]{init_method}[/code]\n'
message += f'  of type [code]{dtype}[/code]\n'
message += f'  using the [code]{backend}[/code] backend.'
print(message)

array = create_array(shape, dtype=dtype, init_method=init_method, backend=backend)
print(f'Array : {array}')

numpy_array = np.ones((3, 3))
process_array(numpy_array)  # Outputs: Processing a NumPy array

dask_array = da.from_array(numpy_array, chunks=(2, 2))
process_array(dask_array)  # Outputs: Processing a Dask array

if CUPY_AVAILABLE:
    cupy_array = cp.ones((3, 3))
    process_array(cupy_array)  # Outputs: Processing a CuPy array if CuPy is available
else:
    print("CuPy is not installed. Skipping CuPy array processing.")
