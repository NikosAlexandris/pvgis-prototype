from dataclasses import dataclass


@dataclass(frozen=True)
class EccentricityCorrectionFactor:
    value: float = 0.03344
    unit: str = 'radians'


@dataclass(frozen=True)
class PerigeeOffset:
    value: float = 0.048869
    unit: str = 'radians'


@dataclass(frozen=True)
class RefractedSolarZenith:
    value: float = 1.5853349194640094
    unit: str = 'radians'


@dataclass(frozen=True)
class AtmosphericRefraction:
    value: float
    unit: str


@dataclass(frozen=True)
class SurfaceTilt:
    value: float = 0
    unit: str = 'radians'


@dataclass(frozen=True)
class SurfaceOrientation:
    value: float = 180
    unit: str = 'radians'


@dataclass(frozen=True)
class Latitude:
    value: float
    unit: str


@dataclass(frozen=True)
class Longitude:
    value: float
    unit: str


@dataclass(frozen=True)
class RelativeLongitude:
    value: float
    unit: str


@dataclass(frozen=True)
class SolarTime:
    value: float
    unit: str


@dataclass(frozen=True)
class TrueSolarTime:
    value: float
    unit: str


@dataclass(frozen=True)
class EquationOfTime:
    value: float
    unit: str


@dataclass(frozen=True)
class FractionalYear:
    value: float
    unit: str


@dataclass(frozen=True)
class TimeOffset:
    value: float
    unit: str


@dataclass(frozen=True)
class EventTime:
    value: float
    unit: str


@dataclass(frozen=True)
class HourAngle:
    value: float
    unit: str


@dataclass(frozen=True)
class HourAngleSunrise:
    value: float
    unit: str


@dataclass(frozen=True)
class SolarHourAngle:
    value: float
    unit: str


@dataclass(frozen=True)
class SolarAltitude:
    value: float
    unit: str


@dataclass(frozen=True)
class SolarAzimuth:
    value: float
    unit: str


@dataclass(frozen=True)
class CompassSolarAzimuth:
    value: float
    unit: str


@dataclass(frozen=True)
class SolarDeclination:
    value: float = 0
    unit: str = 'radians'


@dataclass(frozen=True)
class SolarIncidence:
    value: float
    unit: str


@dataclass(frozen=True)
class SolarZenith:
    value: float
    unit: str


@dataclass(frozen=True)
class SolarPosition:
    value: float
    unit: str

@dataclass(frozen=True)
class HorizonHeight:
    value: float
    unit: str