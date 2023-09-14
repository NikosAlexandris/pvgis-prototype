import yaml
from pydantic import BaseModel
from typing import Optional
from devtools import debug
from pathlib import Path
from pvgisprototype.constants import PARAMETERS_YAML_FILE
import numpy as np


def model_hash(self):
    return hash(tuple(sorted(self.dict().items())))



@property
def degrees_property(self):
    """Instance property to convert radians to degrees"""
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
    """Instance property to convert degrees to radians"""
    if self.value is not None:
        if self.unit == 'radians':
            return self.value
        elif self.unit == 'degrees':
            return np.radians(self.value)
        else:
            return None
    else:
        return None

    if self.unit == 'radians':
        return self.value
    else:  # degrees
        return np.radians(self.value)


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
                **default_values,
            }
        )
        globals()[model_name] = model_class

package_root = Path(__file__).resolve().parent
parameters_yaml_file_path = package_root / 'validation' / PARAMETERS_YAML_FILE
generate_dataclass_models(parameters_yaml_file_path)