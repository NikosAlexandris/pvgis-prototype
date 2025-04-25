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
    "ndarray": NpNDArray,
    "ndarray | None": NpNDArray | None,
    "ndarray | float": NpNDArray | float,
    "ndarray | float | None": NpNDArray | float | None,
    "xarray": DataArray,
    "Tuple[float, float]": Tuple[float, float],
    "Tuple[Longitude, Latitude]": Tuple[float, float],
    "Tuple[Longitude, Latitude, Elevation]": Tuple[float, float, float],
    "DatetimeIndex": DatetimeIndex,
    "Elevation": float,
    "SurfaceOrientation": float,
    "SurfaceTilt": float,
}
