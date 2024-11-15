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
from typing import Tuple, Dict, Type, Any

import numpy
from pandas import DatetimeIndex, Timedelta, TimedeltaIndex, Timestamp, to_timedelta
from pydantic import BaseModel, ConfigDict
from pydantic_numpy import NpNDArray
from pydantic_numpy.model import NumpyModel
from xarray import DataArray

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
    "str | None": str | None,
    "ndarray": NpNDArray,
    "ndarray | float": NpNDArray | float,
    "ndarray | float | None": NpNDArray | float | None,
    "xarray": DataArray,
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


def _custom_getattr(self, attribute_name):
    """Optimized custom getattr function with pre-cached property functions."""
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
    def get_data_model(data_model_name: str, data_model_definitions: dict):
        if data_model_name not in DataModelFactory._cache:
            DataModelFactory._cache[data_model_name] = (
                DataModelFactory._generate_data_model(
                    data_model_name, data_model_definitions
                )
            )
        return DataModelFactory._cache[data_model_name]

    def get_cached_model(data_model_name: str) -> Type[BaseModel]:
        """
        Retrieve a model by name from the cache.
        """
        if data_model_name not in DataModelFactory._cache:
            raise ValueError(f"Model {data_model_name} has not been created.")
        return DataModelFactory._cache[data_model_name]

    @staticmethod
    def _hashable_array(array):
        try:
            # Assume a NumPy array and convert it to bytes for hashing
            return hash(array.tobytes())

        except AttributeError:
            # If it's not an array or doesn't have the 'tobytes' method, hash normally
            return hash(array)

    @staticmethod
    def _generate_hash_function(fields, annotations):
        def hash_model(self):
            # Use a single comprehension for `hash_values`, avoid redundant `getattr` calls
            hash_values = tuple(
                (
                    DataModelFactory._hashable_array(value)
                    if isinstance(value, numpy.ndarray)
                    or annotations[field] == NpNDArray
                    else hash(value)
                )
                for field in fields
                for value in [getattr(self, field)]
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

                if isinstance(self_value, numpy.ndarray) and isinstance(
                    other_value, numpy.ndarray
                ):
                    if not numpy.array_equal(self_value, other_value):
                        return False
                else:
                    if self_value != other_value:
                        return False
            return True

        return eq_model

    @staticmethod
    def generate_data_models(data_model_definitions: Dict[str, Dict]) -> None:
        """
        Generate data models starting with simple models that depend solely on
        Python-native data structures, then build complex models that may reuse
        simple models.
        """
        models_to_generate = set(data_model_definitions.keys())

        # Generate models that rely solely on standard types
        for data_model_name, fields in list(data_model_definitions.items()):
            if DataModelFactory._is_simple_model(fields):
                DataModelFactory._cache[data_model_name] = (
                    DataModelFactory._generate_data_model(data_model_name, fields)
                )
                models_to_generate.remove(data_model_name)

        # Generate complex models by resolving dependencies
        while models_to_generate:
            generated_any_models = False

            for data_model_name in list(models_to_generate):
                fields = data_model_definitions[data_model_name]

                # Create the model if dependencies resolved
                if DataModelFactory._can_generate_complex_model(fields):
                    DataModelFactory._cache[data_model_name] = (
                        DataModelFactory._generate_data_model(data_model_name, fields)
                    )
                    models_to_generate.remove(data_model_name)
                    generated_any_models = True

            # Prevent infinite loop if dependencies cannot be resolved
            if not generated_any_models:
                raise ValueError(
                    "Circular or unresolved dependencies detected among models."
                )

    @staticmethod
    def _is_simple_model(fields: Dict[str, Any]) -> bool:
        """
        Check if a model is a simple one by verifying if all field types are standard.
        """
        return all(field_data["type"] in type_mapping for field_data in fields.values())

    @staticmethod
    def _can_generate_complex_model(fields: Dict[str, Any]) -> bool:
        """
        Determine if a model can be generated by checking if all custom types it depends on have already been generated and cached.
        """
        for field_data in fields.values():
            field_type = field_data["type"]
            if (
                field_type not in type_mapping
                and field_type not in DataModelFactory._cache
            ):
                # Field type in question does not yet exist, thus we cannot generate this complex model
                return False
        return True

    @staticmethod
    def _generate_data_model(
        data_model_name: str, data_model_definitions: Dict
    ) -> Type[BaseModel]:
        """
        Generate a Pydantic model with the specified fields, handling custom types, validation, and conversion functions as necessary.
        """
        fields = []
        annotations = {}
        default_values = {}
        use_numpy_model = False

        # Consume data model definitions
        for field_name, field_data in data_model_definitions[data_model_name].items():
            field_type = field_data["type"]

            if field_type in type_mapping:
                annotations[field_name] = type_mapping[field_type]

                if DataModelFactory._is_np_ndarray_type(type_mapping[field_type]):
                    use_numpy_model = True

            elif field_type in DataModelFactory._cache:
                # If it's a complex type already generated, use that model
                annotations[field_name] = DataModelFactory._cache[field_type]

            else:
                raise ValueError(f"Unknown field type for {field_name}: {field_type}")

            if "initial" in field_data:
                default_values[field_name] = field_data["initial"]
        # Define additional model properties
        base_model = NumpyModel if use_numpy_model else BaseModel
        model_attributes = {
            "__getattr__": _custom_getattr,
            "__annotations__": annotations,
            "__module__": __package__.split(".")[0],
            "__qualname__": data_model_name,
            "__hash__": DataModelFactory._generate_hash_function(fields, annotations),
            "model_config": ConfigDict(arbitrary_types_allowed=True),
            "__eq__": DataModelFactory._generate_alternative_eq_method(fields),
            **default_values,
        }

        return base_model.__class__(data_model_name, (base_model,), model_attributes)
