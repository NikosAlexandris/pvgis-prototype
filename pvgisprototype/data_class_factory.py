from pydantic import BaseModel
from pydantic_numpy import NpNDArray
from pydantic_numpy.model import NumpyModel
from pvgisprototype.constants import RADIANS, DEGREES
from typing import Optional, Union, Tuple
import numpy as np
from math import pi
from pandas import DatetimeIndex
from pydantic import ConfigDict


type_mapping = {
    'None': None,
    'int': int,
    'float': float,
    'Optional[float]': Optional[float],
    'str': str,
    'list': list,
    'dict': dict,
    'ndarray': NpNDArray,
    'Union[ndarray, float]': Union[NpNDArray, float],
    'Tuple[Longitude, Latitude]': Tuple[float, float],
    'Elevation': float,
    'SurfaceOrientation': float,
    'SurfaceTilt': float,
    'DatetimeIndex': DatetimeIndex
}


def _radians_to_minutes(radians):
    return (1440 / (2 * pi)) * radians


def _degrees_to_minutes(degrees):
    radians = np.radians(degrees)
    return _radians_to_minutes(radians)


def _degrees_to_timedelta(degrees):
    return degrees / 15.0


def _radians_to_timedelta(radians):
    degrees = np.degrees(radians)
    return _degrees_to_timedelta(degrees)


def _timestamp_to_hours(timestamp):
    return (
        timestamp.hour
        + timestamp.minute / 60
        + timestamp.second / 3600
        + timestamp.microsecond / 3600000000
    )


def _timestamp_to_minutes(timestamp):
    total_seconds = timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second
    return total_seconds / 60


def _sun_to_plane(self):
    from pvgisprototype import SolarIncidence
    if isinstance(self, SolarIncidence):
        if self.definition == SolarIncidence().definition_complementary:
            return self
        else:
            if self.unit == DEGREES:
                return 90 - self.degrees
            if self.unit == RADIANS:
                return pi/2 - self.radians


def complementary_incidence_angle_property(self):
    from pvgisprototype import SolarIncidence
    if isinstance(self, SolarIncidence):
        return _sun_to_plane(self)


def minutes_property(self):
    if self.unit == "minutes":
        return self.value
    else:
        return None


def timedelta_property(self):
    """Instance property to convert to timedelta"""
    if self.unit == RADIANS:
        return _radians_to_timedelta(self.value)
    elif self.unit == DEGREES:
        return _degrees_to_timedelta(self.value)
    elif self.unit == "timedelta":
        return self.value
    else:
        return None


def as_minutes_property(self):
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


def timestamp_property(self):
    """Instance property to convert to time (timestamp)"""
    if self.unit == "timestamp":
        return self.value
    else:
        return None


def as_hours_property(self):
    """Instance property to convert to hours"""
    if self.unit == "hours":
        return self.value
    elif self.unit == "timestamp":
        return _timestamp_to_hours(self.value)
    else:
        return None


def degrees_property(self):
    """Instance property to convert to degrees"""
    if self.value is not None:
        if self.unit == DEGREES:
            return self.value
        elif self.unit == RADIANS:
            from numbers import Number
            if isinstance(self.value, Number):
                from math import degrees
                return degrees(self.value)
            else:
                return np.degrees(self.value)
        else:
            return None
    else:
        return None


def radians_property(self):
    """Instance property to convert to radians"""
    if self.value is not None:
        if self.unit == RADIANS:
            return self.value
        elif self.unit == DEGREES:
            from numbers import Number
            if isinstance(self.value, Number):
                from math import radians
                return radians(self.value)
            else:
                return np.radians(self.value)
        else:
            return None
    else:
        return None


def _custom_getattr(self, attribute_name):
    property_functions = {
        "radians": radians_property,
        "degrees": degrees_property,
        "complementary" : complementary_incidence_angle_property,
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


def _custom_getstate(self):
    state = self.__dict__.copy()
    # Convert numpy arrays to bytes if necessary
    if isinstance(state["value"], np.ndarray):
        state["value"] = (
            state["value"].tobytes(),
            state["value"].dtype,
            state["value"].shape,
        )
    return state


def _custom_setstate(self, state):
    if isinstance(state["value"], tuple) and len(state["value"]) == 3:
        # Convert bytes back to numpy array
        content, dtype, shape = state["value"]
        state["value"] = np.frombuffer(content, dtype=dtype).reshape(shape)
    self.__dict__.update(state)


class DataClassFactory:
    _cache = {}

    @staticmethod
    def get_data_class(model_name, parameters):
        if model_name not in DataClassFactory._cache:
            DataClassFactory._cache[model_name] = DataClassFactory._generate_class(
                model_name, parameters
            )
        return DataClassFactory._cache[model_name]


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
                    DataClassFactory._hashable_array(getattr(self, field))
                    if isinstance(getattr(self, field), np.ndarray)
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
                if DataClassFactory._is_np_ndarray_type(type_mapping[field_type]):
                    use_numpy_model = True
                    
            if "initial" in field_data:
                default_values[field_name] = field_data["initial"]

        base_class = NumpyModel if use_numpy_model else BaseModel
        class_attributes = {
            "__getattr__": _custom_getattr,
            #"__getstate__": _custom_getstate,
            #"__setstate__": _custom_setstate,
            "__annotations__": annotations,
            "__module__": __package__,
            "__qualname__": model_name,
            "__hash__": DataClassFactory._generate_hash_function(fields, annotations),
            "model_config": ConfigDict(arbitrary_types_allowed=True),
            **default_values,
        }
        return base_class.__class__(model_name, (base_class,), class_attributes)
