from pathlib import Path
from pvgisprototype.constants import PARAMETERS_YAML_FILE
from pvgisprototype import generate_custom_data_classes
import cProfile
import pstats


def main():
    # Call your function here
    package_root = Path(__file__).resolve()
    parameters_yaml_file_path = package_root.parent / PARAMETERS_YAML_FILE
    generate_custom_data_classes(parameters_yaml_file_path)


cProfile.run('main()', 'output_stats')
p = pstats.Stats('output_stats')
p.sort_stats('cumulative').print_stats(10)  # Adjust parameters as needed
