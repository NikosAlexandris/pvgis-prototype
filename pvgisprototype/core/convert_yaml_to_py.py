import yaml

PVGIS_DATA_MODELS_DEFINITIONS_YAML_FILE = "data_model_definitions.yaml"
PVGIS_DATA_MODELS_PYTHON_MODULE = "data_model_definitions.py"


# Read the YAML file
with open(PVGIS_DATA_MODELS_DEFINITIONS_YAML_FILE, "r") as yaml_file:
    pvgis_data_models = yaml.safe_load(yaml_file)

pvgis_data_models_python_module_content = f"# Custom data model definitions : {PVGIS_DATA_MODELS_PYTHON_MODULE}\n\nPVGIS_DATA_MODEL_DEFINITIONS = {pvgis_data_models}\n"

# Write to Python module
with open(PVGIS_DATA_MODELS_PYTHON_MODULE, "w") as python_module:
    python_module.write(pvgis_data_models_python_module_content)
