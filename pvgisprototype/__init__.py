from devtools import debug
import yaml
from pathlib import Path
from pvgisprototype.data_class_factory import DataClassFactory
from pvgisprototype.constants import PARAMETERS_YAML_FILE


def generate_custom_data_classes(yaml_file: str):
    with open(yaml_file, 'r') as f:
        parameters = yaml.safe_load(f)

    for model_name in parameters.keys():
        generated_class = DataClassFactory.get_data_class(model_name, parameters)
        globals()[model_name] = generated_class


package_root = Path(__file__).resolve().parent
parameters_yaml_file_path = package_root / 'validation' / PARAMETERS_YAML_FILE
generate_custom_data_classes(parameters_yaml_file_path)
