import yaml
from pydantic import BaseModel
from devtools import debug
from pathlib import Path
from pvgisprototype.constants import PARAMETERS_YAML_FILE
import numpy as np
from numpy import ndarray
from pvgisprototype.constants import RADIANS, DEGREES
from typing import Union
from datetime import timedelta
from datetime import datetime
from datetime import time


def model_hash(self):
    return hash(tuple(sorted(self.dict().items())))


def _degrees_to_timedelta(degrees):
    return degrees / 15.0


def _radians_to_timedelta(radians):
    degrees = np.degrees(radians)
    return _degrees_to_timedelta(degrees)


def _radians_to_minutes(radians):
    return (1440 / (2 * np.pi)) * radians


def _degrees_to_minutes(degrees):
    radians = np.radians(degrees)
    return _radians_to_minutes(radians)


def _timestamp_to_hours(timestamp):
    return timestamp.hour + timestamp.minute / 60 + timestamp.second / 3600 + timestamp.microsecond / 3600000000


def _timestamp_to_minutes(timestamp):
    total_seconds = timestamp.hour * 3600 + timestamp.minute * 60 + timestamp.second
    return total_seconds / 60


def minutes_property(self):
    if self.unit == 'minutes':
        return self.value
    else:
        return None


def timedelta_property(self):
    """Instance property to convert to timedelta"""
    if self.unit == RADIANS:
        return _radians_to_timedelta(self.value)
    elif self.unit == DEGREES:
        return _degrees_to_timedelta(self.value)
    elif self.unit == 'timedelta':
        return self.value
    else:
        return None


def as_minutes_property(self):
    """Instance property to convert to minutes"""
    if self.unit == 'timedelta':
        value = self.value.total_seconds() / 60
    elif self.unit == 'datetime':
        value = (self.value.hour * 3600 + self.value.minute * 60 + self.value.second) / 60
    elif self.unit == RADIANS:
        value = _radians_to_minutes(self.value)
    elif self.unit == DEGREES:
        value = _degrees_to_minutes(self.value)
    elif self.unit == 'timestamp':
        value = _timestamp_to_minutes(self.value)
    elif self.unit == 'as_minutes':
        value = self.value
    else:
        value = None
    return value


def datetime_property(self):
    """Instance property to convert to datetime"""
    if self.unit == 'datetime':
        return self.value
    else:
        return None


def timestamp_property(self):
    """Instance property to convert to time (timestamp)"""
    if self.unit == 'timestamp':
        return self.value
    else:
        return None


def as_hours_property(self):
    """Instance property to convert to hours"""
    if self.unit == 'hours':
        return self.value
    elif self.unit == 'timestamp':
        return _timestamp_to_hours(self.value)
    else:
        return None


def minutes_property(self):
    if self.unit == 'minutes':
        return self.value
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


def generate_cutom_data_classes(yaml_file: str):

    def custom_getattr(self, attr_name):
        if attr_name == 'radians':
            value = radians_property(self)
        elif attr_name == 'degrees':
            value = degrees_property(self)
        elif attr_name == 'minutes':
            value = minutes_property(self)
        elif attr_name == 'timedelta':
            value = timedelta_property(self)
        elif attr_name == 'as_minutes':
            value = as_minutes_property(self)
        elif attr_name == 'datetime':
            value = datetime_property(self)
        elif attr_name == 'timestamp':
            value = timestamp_property(self)
        elif attr_name == 'as_hours':
            value = as_hours_property(self)
        else:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attr_name}'")
        
        try:
            if value is None:
                raise AttributeError(f"'{self.__class__.__name__}' object can't have attribute '{attr_name}'")
        except ValueError:
            if not np.any(value):
                raise AttributeError(f"'{self.__class__.__name__}' object can't have attribute '{attr_name}'")
            
        # self.__dict__[name] = value
        # self.__dict__['value'] = value
        # self.__dict__['unit'] = attr_name
        return value

    with open(yaml_file, 'r') as f:
        parameters = yaml.safe_load(f)

    for model_name, fields in parameters.items():
        annotations = {}
        default_values = {}

        for field_name, field_data in fields.items():
            annotations[field_name] = eval(field_data['type'])
            if 'initial' in field_data:
                default_values[field_name] = field_data['initial']

        model_class = BaseModel.__class__(
            model_name,
            (BaseModel,),
            {
                '__getattr__': custom_getattr,
                '__annotations__': annotations,
                '__module__': __name__,
                '__qualname__': model_name,
                '__hash__': model_hash,
                **default_values,
            },
            arbitrary_types_allowed=True,
        )
        globals()[model_name] = model_class


package_root = Path(__file__).resolve().parent
parameters_yaml_file_path = package_root / 'validation' / PARAMETERS_YAML_FILE
generate_cutom_data_classes(parameters_yaml_file_path)
