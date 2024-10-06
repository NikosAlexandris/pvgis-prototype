import yaml

PVGIS_DATA_MODELS_DEFINITIONS_YAML_FILE = "definitions.yaml"
PVGIS_DATA_MODELS_PYTHON_MODULE = "definitions.py"


def convert_yaml_definitions_to_python_dictionary():
    """ """
    # Read the YAML file
    with open(PVGIS_DATA_MODELS_DEFINITIONS_YAML_FILE, "r") as yaml_file:
        pvgis_data_models = yaml.safe_load(yaml_file)

    pvgis_data_models_python_module_content = f"# {PVGIS_DATA_MODELS_PYTHON_MODULE}\n\npvgis_data_models = {pvgis_data_models}\n"

    # Write to Python module
    with open(PVGIS_DATA_MODELS_PYTHON_MODULE, "w") as python_module:
        python_module.write(pvgis_data_models_python_module_content)
