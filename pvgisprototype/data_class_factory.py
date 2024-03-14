from pydantic import BaseModel
from pvgisprototype.constants import RADIANS, DEGREES
from datetime import datetime
from datetime import time
from typing import Union
from typing import Tuple
import numpy as np


type_mapping = {
    'int': int,
    'float': float,
    'str': str,
    'list': list,
    'dict': dict,
    'ndarray': np.ndarray,
    'Union[ndarray, float]': Union[np.ndarray, float],
    'Tuple[Longitude, Latitude]': Tuple[float, float],
    'Elevation': float,
    'SurfaceOrientation': float,
    'SurfaceTilt': float,
}


def _degrees_to_timedelta(degrees):
    return degrees / 15.0


def _degrees_to_minutes(degrees):
    radians = np.radians(degrees)
    return _radians_to_minutes(radians)


def _radians_to_timedelta(radians):
    degrees = np.degrees(radians)
    return _degrees_to_timedelta(degrees)


def _radians_to_minutes(radians):
    return (1440 / (2 * np.pi)) * radians


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
    if self.unit == "timedelta":
        value = self.value.total_seconds() / 60
    elif self.unit == "datetime":
        value = (
            self.value.hour * 3600 + self.value.minute * 60 + self.value.second
        ) / 60
    elif self.unit == RADIANS:
        value = _radians_to_minutes(self.value)
    elif self.unit == DEGREES:
        value = _degrees_to_minutes(self.value)
    elif self.unit == "timestamp":
        value = _timestamp_to_minutes(self.value)
    elif self.unit == "as_minutes":
        value = self.value
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
            return np.radians(self.value)
        else:
            return None
    else:
        return None


def _custom_getattr(self, attr_name):
    property_functions = {
        "radians": radians_property,
        "degrees": degrees_property,
        "minutes": minutes_property,
        "timedelta": timedelta_property,
        "as_minutes": as_minutes_property,
        "datetime": datetime_property,
        "timestamp": timestamp_property,
        "as_hours": as_hours_property,
    }
    value = property_functions.get(attr_name)
    if value:
        return value(self)
    else:
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{attr_name}'"
        )

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
    def _generate_model_hash(model_instance):
        return hash(tuple(sorted(model_instance.dict().items())))

    @staticmethod
    def _generate_class(model_name, parameters):
        annotations = {}
        default_values = {}

        for field_name, field_data in parameters[model_name].items():
            if field_data["type"] in type_mapping:
                annotations[field_name] = type_mapping[field_data["type"]]

            if "initial" in field_data:
                default_values[field_name] = field_data["initial"]

        return BaseModel.__class__(
            model_name,
            (BaseModel,),
            {
                "__getattr__": _custom_getattr,
                "__annotations__": annotations,
                "__module__": __name__,
                "__qualname__": model_name,
                "__hash__": DataClassFactory._generate_model_hash,
                **default_values,
            },
            arbitrary_types_allowed=True,
        )
