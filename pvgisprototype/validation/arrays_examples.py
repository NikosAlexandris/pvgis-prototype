from devtools import debug
import numpy as np
import dask.array as da
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

array = create_array((10, 10), dtype='float64', init_method='ones', backend='numpy')
print(f'{array}')
debug(locals())

numpy_array = np.array([1, 2, 3])
dask_array = da.from_array(numpy_array, chunks=(2,))

process_array(numpy_array)  # Outputs: Processing a NumPy array
process_array(dask_array)   # Outputs: Processing a Dask array
