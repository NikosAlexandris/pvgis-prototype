import yaml
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta
from datetime import datetime
from datetime import time
from devtools import debug
from pathlib import Path
from pvgisprototype.constants import PARAMETERS_YAML_FILE
import numpy as np


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



@property
def degrees_property(self):
    """Instance property to convert to degrees"""
    if self.value is not None:
        if self.unit == 'degrees':
            return self.value
        elif self.unit == 'radians':
            return np.degrees(self.value)
        else:
            return None
    else:
        return None


@property
def radians_property(self):
    """Instance property to convert to radians"""
    if self.value is not None:
        if self.unit == 'radians':
            return self.value
        elif self.unit == 'degrees':
            return np.radians(self.value)
        else:
            return None
    else:
        return None


@property
def timedelta_property(self):
    """Instance property to convert to timedelta"""
    if self.unit == 'radians':
        return _radians_to_timedelta(self.value)
    elif self.unit == 'degrees':
        return _degrees_to_timedelta(self.value)
    elif self.unit == 'timedelta':
        return self.value
    else:
        return None


@property
def as_minutes_property(self):
    """Instance property to convert to minutes"""
    if self.unit == 'timedelta':
        return self.value.total_seconds() / 60
    elif self.unit == 'datetime':
        return (self.value.hour * 3600 + self.value.minute * 60 + self.value.second) / 60
    elif self.unit == 'radians':
        return _radians_to_minutes(self.value)
    elif self.unit == 'degrees':
        return _degrees_to_minutes(self.value)
    else:
        return None


@property
def datetime_property(self):
    """Instance property to convert to datetime"""
    if self.unit == 'datetime':
        return self.value
    else:
        return None


@property
def timestamp_property(self):
    """Instance property to convert to time (timestamp)"""
    if self.unit == 'timestamp':
        return self.value
    else:
        return None


@property
def as_hours_property(self):
    """Instance property to convert to hours"""
    if self.unit == 'hours':
        return self.value
    elif self.unit == 'timestamp':
        return _timestamp_to_hours(self.value)
    else:
        return None



def generate_dataclass_models(yaml_file: str):

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
                **annotations,
                '__annotations__': annotations,
                '__module__': __name__,
                '__qualname__': model_name,
                '__hash__': model_hash,
                'degrees': degrees_property,
                'radians': radians_property,
                'timedelta': timedelta_property,
                'as_minutes': as_minutes_property,
                'datetime': datetime_property,
                'timestamp': timestamp_property,
                'as_hours': as_hours_property,
                **default_values,
            }
        )
        globals()[model_name] = model_class

package_root = Path(__file__).resolve().parent
parameters_yaml_file_path = package_root / 'validation' / PARAMETERS_YAML_FILE
generate_dataclass_models(parameters_yaml_file_path)




# longitude = Longitude(value=40, unit='degrees')
# print(longitude.timedelta)