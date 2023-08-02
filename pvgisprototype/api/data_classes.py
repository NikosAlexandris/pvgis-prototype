from typing import Union
from dataclasses import dataclass
# from dataclasses import is_dataclass


# class CalculationsSupport:
#     value: Union[float, int]

#     def __add__(self, other):
#         if isinstance(other, (int, float)):
#             return self.value + other
#         elif is_dataclass(other):
#             return self.value + other.value
#         else:
#             raise TypeError("Unsupported operand types for +: '{}' and '{}'".format(
#                 self.__class__, type(other)))

#     __radd__ = __add__

#     def __mul__(self, other):
#         if isinstance(other, (int, float)):
#             return self.value * other
#         elif is_dataclass(other):
#             return self.value * other.value
#         else:
#             raise TypeError("Unsupported operand types for *: '{}' and '{}'".format(
#                 self.__class__, type(other)))

#     __rmul__ = __mul__

#     def __truediv__(self, other):
#         if isinstance(other, (int, float)):
#             return self.value / other
#         elif is_dataclass(other):
#             return self.value / other.value
#         else:
#             raise TypeError("Unsupported operand types for /: '{}' and '{}'".format(
#                 self.__class__, type(other)))

#     __rtruediv__ = lambda self, other: other / self.value if isinstance(
#         other, (int, float)) else other.value / self.value

#     def __sub__(self, other):
#         if isinstance(other, (int, float)):
#             return self.value - other
#         elif is_dataclass(other):
#             return self.value - other.value
#         else:
#             raise TypeError("Unsupported operand types for -: '{}' and '{}'".format(
#                 self.__class__, type(other)))

#     __rsub__ = lambda self, other: other - self.value if isinstance(
#         other, (int, float)) else other.value - self.value


@dataclass(frozen=True)
class OrbitalEccentricity:
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