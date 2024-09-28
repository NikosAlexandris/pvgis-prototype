from functools import wraps

import numpy
from cachetools import cached
from cachetools.keys import hashkey
from pandas import Timestamp, DatetimeIndex, Index

from pvgisprototype import (
    LinkeTurbidityFactor,
    OpticalAirMass,
    RefractedSolarAltitude,
    SolarAltitude,
    SolarHourAngle,
    SurfaceOrientation,
    SurfaceTilt,
)


def generate_custom_hashkey(*args, **kwargs):
    args = tuple(
        (
            # tuple(arg.tolist()) if isinstance(arg, numpy.ndarray)
            # tuple(str(id(arg))) if isinstance(arg, numpy.ndarray)
            # else str(arg)
            str(arg)
            if isinstance(
                arg,
                (
                    list,
                    numpy.ndarray,
                    Timestamp,
                    DatetimeIndex,
                    LinkeTurbidityFactor,
                    OpticalAirMass,
                    RefractedSolarAltitude,
                    SolarAltitude,
                    Index,
                    SolarHourAngle,
                    SurfaceOrientation,
                    SurfaceTilt,
                ),
            )
            else arg
        )
        for arg in args
    )
    kwargs = {
        k: (
            # tuple(v.tolist()) if isinstance(v, numpy.ndarray)
            # tuple(str(id(v))) if isinstance(v, numpy.ndarray)
            # else str(v)
            str(v)
            if isinstance(
                v,
                (
                    list,
                    numpy.ndarray,
                    Timestamp,
                    DatetimeIndex,
                    LinkeTurbidityFactor,
                    OpticalAirMass,
                    RefractedSolarAltitude,
                    SolarAltitude,
                    Index,
                    SolarHourAngle,
                    SurfaceOrientation,
                    SurfaceTilt,
                ),
            )
            else v
        )
        for k, v in kwargs.items()
    }
    return hashkey(*args, **kwargs)


def custom_cached(func):
    @wraps(func)
    @cached(cache={}, key=generate_custom_hashkey)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
