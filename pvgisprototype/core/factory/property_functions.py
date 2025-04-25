"""
Attention

The 'module'

    from pvgisprototype.core.data_model.definitions import PVGIS_DATA_MODEL_DEFINITIONS

needs to pre-exist, at the current setup, even for its "own" generation via the
script 

    pvgisprototype/core/data_model/generate_definitions.py !

Just create one, in case, even with an empty dictionary names
PVGIS_DATA_MODEL_DEFINITIONS. Then run the generation script, simply via

```
python generate_definitions.py
````

"""
from math import pi
from typing import Dict
import numpy
from pandas import Timedelta, TimedeltaIndex, Timestamp, to_timedelta
from pvgisprototype.core.data_model.definitions import PVGIS_DATA_MODEL_DEFINITIONS
from pydantic_numpy import NpNDArray

from pvgisprototype.constants import DEGREES, RADIANS


def _radians_to_minutes(radians: float | NpNDArray) -> float | NpNDArray:
    return (1440 / (2 * pi)) * radians


def _degrees_to_minutes(degrees: float | NpNDArray) -> float | NpNDArray:
    radians = numpy.radians(degrees)
    return _radians_to_minutes(radians)


def _degrees_to_timedelta(degrees: float | NpNDArray) -> Timedelta | TimedeltaIndex:
    if isinstance(degrees, float):
        return Timedelta(degrees / 15, unit='h')
    elif isinstance(degrees, ndarray):
        return to_timedelta(degrees_float / 15, unit='h')
    else:
        raise TypeError(f"Unsupported input type: {type(degrees)}")


def _radians_to_timedelta(radians: float | NpNDArray) -> Timedelta | TimedeltaIndex:
    degrees = numpy.degrees(radians)
    return _degrees_to_timedelta(degrees)


def _timestamp_to_hours(timestamp: Timestamp | NpNDArray) -> float | NpNDArray:
    if isinstance(timestamp, Timestamp):
        return (
            timestamp.hour
            + timestamp.minute / 60
            + timestamp.second / 3600
            + timestamp.microsecond / 3600000000
        )
    elif isinstance(timestamp, NpNDArray):
        return numpy.vectorize(lambda t: (
            t.hour + t.minute / 60 + t.second / 3600 + t.microsecond / 3600000000))(timestamp)


def _timestamp_to_minutes(timestamp: Timestamp | NpNDArray) -> float | NpNDArray:
    if isinstance(timestamp, Timestamp):
        total_seconds = timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second
        return total_seconds / 60
    elif isinstance(timestamp, NpNDArray):
        return numpy.vectorize(lambda t: (
            t.hour * 3600 + t.minute * 60 + t.second) / 60)(timestamp)


def _sun_to_plane(self):
    from pvgisprototype import SolarIncidence

    if isinstance(self, SolarIncidence):
        if self.definition == SolarIncidence().definition_complementary:
            return self
        else:
            if self.unit == DEGREES:
                return 90 - self.degrees
            if self.unit == RADIANS:
                return pi / 2 - self.radians


def complementary_incidence_angle_property(self):
    from pvgisprototype import SolarIncidence

    if isinstance(self, SolarIncidence):
        return _sun_to_plane(self)


def minutes_property(self: float | NpNDArray | None) -> float | NpNDArray | None:
    if self.unit == "minutes":
        return self.value
    else:
        return None


def timedelta_property(self) -> Timedelta | TimedeltaIndex | None:
    """Instance property to convert to timedelta"""
    if self.unit == RADIANS:
        return _radians_to_timedelta(self.value)
    elif self.unit == DEGREES:
        return _degrees_to_timedelta(self.value)
    elif self.unit == "timedelta":
        return self.value
    else:
        return None


def as_minutes_property(self) -> float | NpNDArray | None:
    """Instance property to convert to minutes"""
    if self.unit == "minutes":
        value = self.value
    elif self.unit == "datetime":
        value = (
            self.value.hour * 3600 + self.value.minute * 60 + self.value.second
        ) / 60
    elif self.unit == "timestamp":
        value = _timestamp_to_minutes(self.value)
    elif self.unit == "timedelta":
        value = self.value.total_seconds() / 60
    elif self.unit == RADIANS:
        value = _radians_to_minutes(self.value)
    elif self.unit == DEGREES:
        value = _degrees_to_minutes(self.value)
    else:
        value = None
    return value


def datetime_property(self):
    """Instance property to convert to datetime"""
    if self.unit == "datetime":
        return self.value
    else:
        return None


def timestamp_property(self) -> Timestamp | None:
    """Instance property to convert to time (timestamp)"""
    if self.unit == "timestamp":
        return self.value
    else:
        return None


def as_hours_property(self) -> float | NpNDArray | None:
    """Instance property to convert to hours"""
    if self.unit == "hours":
        return self.value
    elif self.unit == "timestamp":
        return _timestamp_to_hours(self.value)
    else:
        return None


def degrees_property(self) -> float | NpNDArray | None:
    """Instance property to convert to degrees."""
    if self.value is None:
        return None

    if self.unit == DEGREES:
        return self.value

    elif self.unit == RADIANS:
        if isinstance(self.value, (int, float)):
            from math import degrees
            return degrees(self.value)

        if isinstance(self.value, numpy.ndarray):
            return numpy.degrees(self.value)

    return None


def radians_property(self) -> float | NpNDArray | None:
    """Instance property to convert to radians"""
    if self.value is None:
        return None

    if self.unit == RADIANS:
        return self.value

    elif self.unit == DEGREES:
        if isinstance(self.value, (int, float)):
            from math import radians
            return radians(self.value)

        if isinstance(self.value, numpy.ndarray):
            return numpy.radians(self.value)

    return None


def get_model_definition(self) -> Dict:
    """Retrieve the definition of a model from the global definitions."""
    if self.data_model_name not in PVGIS_DATA_MODEL_DEFINITIONS:
        raise ValueError(f"No definition found for model: {self.data_model_name}")
    return PVGIS_DATA_MODEL_DEFINITIONS[self.data_model_name]


PROPERTY_FUNCTIONS = {
    "radians": radians_property,
    "degrees": degrees_property,
    "complementary": complementary_incidence_angle_property,
    "minutes": minutes_property,
    "timedelta": timedelta_property,
    "as_minutes": as_minutes_property,
    "datetime": datetime_property,
    "timestamp": timestamp_property,
    "as_hours": as_hours_property,
    "model_definition": get_model_definition,
}
