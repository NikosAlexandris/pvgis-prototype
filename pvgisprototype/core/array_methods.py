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
from typing import Any
from pvgisprototype.constants import DATA_TYPE_DEFAULT
from pvgisprototype.core.arrays import create_array


def create_array_method(
    self,
    shape,
    dtype: str = DATA_TYPE_DEFAULT,
    init_method: bool | int | float | str = "zeros",
    backend: str = "numpy",
    use_gpu: bool = False,
) -> Any:
    """Helper function to create an instance with an empty array"""
    return self(
        value=create_array(
            shape=shape,
            dtype=dtype,
            init_method=init_method,
            backend=backend,
            use_gpu=use_gpu,
        )
    )
    # self.value = create_array(
    #     shape=shape,
    #     dtype=dtype,
    #     init_method=init_method,
    #     backend=backend,
    #     use_gpu=use_gpu,
    # )


def fill_array_method(
    # cl_ss,
    self,
    shape,
    dtype: str = DATA_TYPE_DEFAULT,
    init_method: bool | int | float | str = "zeros",
    backend: str = "numpy",
    use_gpu: bool = False,
) -> Any:
    """Helper function to create an instance with an empty array"""
    # return cl_ss(
    #     value=create_array(
    #         shape=shape,
    #         dtype=dtype,
    #         init_method=init_method,
    #         backend=backend,
    #         use_gpu=use_gpu,
    #     )
    # )
    self.value = create_array(
        shape=shape,
        dtype=dtype,
        init_method=init_method,
        backend=backend,
        use_gpu=use_gpu,
    )


ARRAY_METHODS = {
    "create_array": create_array_method,
    "fill_array": fill_array_method,
}
