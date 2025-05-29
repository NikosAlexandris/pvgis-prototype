from pvgisprototype.core.factory.data_model import DataModelFactory
from pvgisprototype.core.data_model.definitions import PVGIS_DATA_MODEL_DEFINITIONS


def generate_data_models(data_model_definitions: dict):
    for data_model_name in data_model_definitions.keys():
        globals()[data_model_name] = DataModelFactory.get_data_model(
                data_model_name=data_model_name,
                data_model_definitions=data_model_definitions
                )

generate_data_models(PVGIS_DATA_MODEL_DEFINITIONS)
