from pvgisprototype.core.data_model_factory import DataModelFactory
from pvgisprototype.core.data_model_definitions import PVGIS_DATA_MODEL_DEFINITIONS


def generate_data_models(definitions: dict):
    for class_name in definitions.keys():
        generated_class = DataModelFactory.get_data_class(class_name, definitions)
        globals()[class_name] = generated_class


generate_data_models(PVGIS_DATA_MODEL_DEFINITIONS)
