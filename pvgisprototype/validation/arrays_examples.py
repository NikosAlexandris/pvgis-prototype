from rich import print
from devtools import debug
import numpy as np
import dask.array as da
# import cupy as cp
from pvgisprototype.validation.arrays import NDArrayBackend
from pvgisprototype.validation.arrays import create_array


def process_array(array):
    backend = NDArrayBackend.from_object(array)

    if backend == NDArrayBackend.NUMPY:
        print("Processing a NumPy array")
        # Perform NumPy-specific operations
    elif backend == NDArrayBackend.CUPY:
        print("Processing a CuPy array")
        # Perform CuPy-specific operations
    elif backend == NDArrayBackend.DASK:
        print("Processing a Dask array")
        # Perform Dask-specific operations
    else:
        raise ValueError("Unknown array backend")

shape = (10, 10)
dtype='float64'
initialisation_method = 'ones'
array_backend = 'numpy'

print(f'[underline]Example[/underline]')
message = f'Create an array of :\n'
message += f'  shape [code]{shape}[/code]\n'
message += f'  method [code]{initialisation_method}[/code]\n'
message += f'  of type [code]{dtype}[/code]\n'
message += f'  using the [code]{array_backend}[/code] backend.'
print(message)
array = create_array((10, 10), dtype='float64', init_method='ones', backend='numpy')
print()
print(f'Array : {array}')

# print(f'Everything in this session so far :')
# debug(locals())

numpy_array = np.array([1, 2, 3])
process_array(numpy_array)  # Outputs: Processing a NumPy array

dask_array = da.from_array(numpy_array, chunks=(2,))
process_array(dask_array)   # Outputs: Processing a Dask array

# cupy_array = cp.array([1, 2, 3])
# process_array(cupy_array)
