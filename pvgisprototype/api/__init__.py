from devtools import debug
from pathlib import Path
from pvgisprototype.api.data_classes import generate_dataclass_models
from pvgisprototype.constants import PARAMETERS_YAML_FILE

package_root = Path(__file__).resolve().parent
parameters_yaml_file_path = package_root / PARAMETERS_YAML_FILE
generate_dataclass_models(parameters_yaml_file_path)
