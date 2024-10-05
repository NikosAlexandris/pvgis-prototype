import yaml

PVIS_DATA_CLASSES_DEFINITIONS_YAML_FILE = "pvis_data_classes_definitions.yaml"
PVIS_DATA_CLASSES_PYTHON_MODULE = "pvis_data_classes_definitions.py"


# Read the YAML file
with open(PVIS_DATA_CLASSES_DEFINITIONS_YAML_FILE, "r") as yaml_file:
    pvis_data_classes = yaml.safe_load(yaml_file)

pvis_data_classes_python_module_content = (
    f"# {PVIS_DATA_CLASSES_PYTHON_MODULE}\n\npvis_data_classes = {pvis_data_classes}\n"
)

# Write to Python module
with open(PVIS_DATA_CLASSES_PYTHON_MODULE, "w") as python_module:
    python_module.write(pvis_data_classes_python_module_content)
