from cachetools.keys import hashkey
from pandas import DatetimeIndex, Index
from pvgisprototype import LinkeTurbidityFactor
from pvgisprototype import OpticalAirMass
from pvgisprototype import RefractedSolarAltitude
from pvgisprototype import SolarAltitude
from pvgisprototype import SolarHourAngle


def custom_hashkey(*args, **kwargs):
    args = tuple(
        (
            str(arg)
            if isinstance(
                arg,
                (
                    DatetimeIndex,
                    LinkeTurbidityFactor,
                    OpticalAirMass,
                    RefractedSolarAltitude,
                    SolarAltitude,
                    Index,
                    SolarHourAngle,
                ),
            )
            else arg
        )
        for arg in args
    )
    kwargs = {
        k: (
            str(v)
            if isinstance(
                v,
                (
                    DatetimeIndex,
                    LinkeTurbidityFactor,
                    OpticalAirMass,
                    RefractedSolarAltitude,
                    SolarAltitude,
                    Index,
                    SolarHourAngle,
                ),
            )
            else v
        )
        for k, v in kwargs.items()
    }
    return hashkey(*args, **kwargs)
