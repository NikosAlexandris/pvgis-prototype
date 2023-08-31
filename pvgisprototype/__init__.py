from devtools import debug
import yaml
from pydantic import BaseModel
from typing import Optional
from devtools import debug
import yaml
from pydantic import BaseModel
from typing import Optional
from devtools import debug
from pathlib import Path
# from pvgisprototype.validation.data_classes import generate_dataclass_models
from pvgisprototype.constants import PARAMETERS_YAML_FILE


def model_hash(self):
    return hash(tuple(sorted(self.dict().items())))


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
                **default_values,
            }
        )
        # debug(locals())
        globals()[model_name] = model_class
        # setattr(data_classes, model_name, model_class)

package_root = Path(__file__).resolve().parent
parameters_yaml_file_path = package_root / 'validation' / PARAMETERS_YAML_FILE
generate_dataclass_models(parameters_yaml_file_path)
