"""
This module defines a factory to generate custom data classes (or else models)
dynamically using Pydantic's `BaseModel`. It includes utilities for unit
conversions (e.g., radians, degrees, timestamps), custom attribute handling,
and validation of model fields. The `DataModelFactory` enables efficient
creation of models with properties like solar incidence angles, coordinates,
and time series data, allowing for flexible data representation and
manipulation.

Key Features

- Dynamic generation of data models with custom attributes.
- Unit conversion utilities (e.g., degrees to radians, timestamps to hours).
- Integration with NumPy for handling array-based fields.
"""

from math import pi
from typing import Tuple

import numpy
from pandas import DatetimeIndex, Timedelta, TimedeltaIndex, Timestamp, to_timedelta
from pydantic import BaseModel, ConfigDict
from pydantic_numpy import NpNDArray
from pydantic_numpy.model import NumpyModel

from pvgisprototype.constants import DEGREES, RADIANS

type_mapping = {
    "None": None,
    "bool": bool,
    "str": str,
    "list": list,
    "dict": dict,
    "int": int,
    "float": float,
    "float | None": float | None,
    "ndarray": NpNDArray,
    "ndarray | float": NpNDArray | float,
    "Tuple[Longitude, Latitude]": Tuple[float, float],
    "DatetimeIndex": DatetimeIndex,
    "Elevation": float,
    "SurfaceOrientation": float,
    "SurfaceTilt": float,
}


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


def _custom_getattr(self, attribute_name):
    property_functions = {
        "radians": radians_property,
        "degrees": degrees_property,
        "complementary": complementary_incidence_angle_property,
        "minutes": minutes_property,
        "timedelta": timedelta_property,
        "as_minutes": as_minutes_property,
        "datetime": datetime_property,
        "timestamp": timestamp_property,
        "as_hours": as_hours_property,
    }
    value = property_functions.get(attribute_name)
    if value:
        return value(self)
    else:
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{attribute_name}'"
        )


class DataModelFactory:
    _cache = {}

    @staticmethod
    def get_data_class(model_name, parameters):
        if model_name not in DataModelFactory._cache:
            DataModelFactory._cache[model_name] = DataModelFactory._generate_class(
                model_name, parameters
            )
        return DataModelFactory._cache[model_name]

    @staticmethod
    def _hashable_array(array):
        try:
            # Assume it's a NumPy array and convert it to bytes for hashing
            return hash(array.tobytes())
        except AttributeError:
            # If it's not an array or doesn't have the 'tobytes' method, hash normally
            return hash(array)

    @staticmethod
    def _generate_hash_function(fields, annotations):
        def hash_model(self):
            # Create a tuple of hashable representations of each field
            hash_values = tuple(
                (
                    DataModelFactory._hashable_array(getattr(self, field))
                    if isinstance(getattr(self, field), numpy.ndarray)
                    or annotations[field] == NpNDArray
                    else hash(getattr(self, field))
                )
                for field in fields
            )
            return hash(hash_values)

        return hash_model

    @staticmethod
    def _is_np_ndarray_type(field_type):
        """Utility function to check if a field type is or involves NpNDArray."""
        # Handle direct type comparisons
        if field_type is NpNDArray:
            return True

        # Handle complex types involving NpNDArray
        from types import GenericAlias

        if isinstance(field_type, GenericAlias):
            # Check if NpNDArray is part of a Union or other complex type
            return NpNDArray in getattr(field_type, "__args__", [])

        return False
    
    @staticmethod
    def _generate_alternative_eq_method(fields):
        def eq_model(self, other):
            if not isinstance(other, self.__class__):
                return False
            for field in fields:
                self_value = getattr(self, field)
                other_value = getattr(other, field)
                if isinstance(self_value, numpy.ndarray) and isinstance(other_value, numpy.ndarray):
                    if not numpy.array_equal(self_value, other_value):
                        return False
                else:
                    if self_value != other_value:
                        return False
            return True

        return eq_model

    @staticmethod
    def _generate_class(model_name, parameters):
        annotations = {}
        default_values = {}
        fields = []
        use_numpy_model = False

        for field_name, field_data in parameters[model_name].items():
            field_type = field_data["type"]
            if field_type in type_mapping:
                annotations[field_name] = type_mapping[field_type]
                fields.append(field_name)
                if DataModelFactory._is_np_ndarray_type(type_mapping[field_type]):
                    use_numpy_model = True

            if "initial" in field_data:
                default_values[field_name] = field_data["initial"]

        base_class = NumpyModel if use_numpy_model else BaseModel
        class_attributes = {
            "__getattr__": _custom_getattr,
            "__annotations__": annotations,
            "__module__": __package__,
            "__qualname__": model_name,
            "__hash__": DataModelFactory._generate_hash_function(fields, annotations),
            "model_config": ConfigDict(arbitrary_types_allowed=True),
            "__eq__": DataModelFactory._generate_alternative_eq_method(fields),
            **default_values,
        }
        return base_class.__class__(model_name, (base_class,), class_attributes)
