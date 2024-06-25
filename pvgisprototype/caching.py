from cachetools.keys import hashkey
from pandas import DatetimeIndex, Index
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype import OpticalAirMass
from pvgisprototype import RefractedSolarAltitude
from pvgisprototype import SolarAltitude
from pvgisprototype import SolarHourAngle
from pvgisprototype import SurfaceOrientation, SurfaceTilt
import numpy

def custom_hashkey(*args, **kwargs):
    args = tuple(
        (
            # tuple(arg.tolist()) if isinstance(arg, numpy.ndarray)
            # tuple(str(id(arg))) if isinstance(arg, numpy.ndarray)
            # else str(arg)
            str(arg)
            if isinstance(
                arg,
                (
                    numpy.ndarray,
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
                    numpy.ndarray,
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
