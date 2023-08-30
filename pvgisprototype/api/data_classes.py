import yaml
from pydantic import BaseModel
from typing import Optional
from pvgisprototype.api import models


def model_hash(self):
    return hash(tuple(sorted(self.dict().items())))


def generate_dataclass_models(yaml_file: str):

    with open(yaml_file, 'r') as f:
        parameters_info = yaml.safe_load(f)

    for model_name, fields in parameters_info.items():
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
                '__module__': "models",
                '__qualname__': model_name,
                '__hash__': model_hash,
                **default_values,
            }
        )
        setattr(models, model_name, model_class)
