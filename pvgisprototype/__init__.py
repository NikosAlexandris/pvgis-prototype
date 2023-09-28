import yaml
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta
from datetime import datetime
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


@property
def degrees_property(self):
    """Instance property to convert radians, timedelta to degrees"""
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
    """Instance property to convert degrees, timedelta to radians"""
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
    """Instance property to convert ... to timedelta"""
    if self.unit == 'radians':
        return _radians_to_timedelta(self.value)
    elif self.unit == 'degrees':
        return _degrees_to_timedelta(self.value)
    elif self.unit == 'timedelta':
        return self.value
    else:
        return None


@property
def minutes_property(self):
    """Instance property to convert timedelta, datetime to minutes"""
    if self.unit == 'timedelta':
        return self.value.total_seconds() / 60
    elif self.unit == 'datetime':
        return (self.value.hour * 3600 + self.value.minute * 60 + self.value.second) / 60
    else:
        return None


@property
def datetime_property(self):
    """Instance property to convert ... to datetime"""
    if self.unit == 'datetime':
        return self.value
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
                'minutes': minutes_property,
                'datetime': datetime_property,
                **default_values,
            }
        )
        globals()[model_name] = model_class

package_root = Path(__file__).resolve().parent
parameters_yaml_file_path = package_root / 'validation' / PARAMETERS_YAML_FILE
generate_dataclass_models(parameters_yaml_file_path)




# longitude = Longitude(value=40, unit='degrees')
# print(longitude.timedelta)