from pathlib import Path
from pvgisprototype.constants import PARAMETERS_YAML_FILE
# from pvgisprototype import generate_custom_data_classes
from pvgisprototype import generate_dataclass_models
from memory_profiler import profile


@profile
def main():
    # Call your function here
    package_root = Path(__file__).resolve()
    parameters_yaml_file_path = package_root.parent / PARAMETERS_YAML_FILE
    # generate_custom_data_classes(parameters_yaml_file_path)
    generate_dataclass_models(parameters_yaml_file_path)


main()
