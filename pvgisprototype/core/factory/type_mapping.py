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
from numpy import ndarray
from xarray import DataArray
from pydantic_numpy import NpNDArray
from pandas import DatetimeIndex 
from typing import Tuple


TYPE_MAPPING = {
    "None": None,
    "bool": bool,
    "bool | None": bool | None,
    "str": str,
    "list": list,
    "dict": dict,
    "set": set,
    "int": int,
    "float": float,
    "float | None": float | None,
    "str | None": str | None,
    "array": NpNDArray,
    "array | None": NpNDArray | None,
    "array | float": NpNDArray | float,
    "array | float | None": NpNDArray | float | None,
    "xarray": DataArray,
    "Tuple[float, float]": Tuple[float, float],
    "Tuple[Longitude, Latitude]": Tuple[float, float],
    "Tuple[Longitude, Latitude, Elevation]": Tuple[float, float, float],
    "DatetimeIndex": DatetimeIndex,
    "Elevation": float,
    "SurfaceOrientation": float,
    "SurfaceTilt": float,
}
