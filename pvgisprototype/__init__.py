from pvgisprototype.data_class_factory import DataClassFactory
from pvgisprototype.validation.parameters_dictionary import parameters


def generate_custom_data_classes(parameters: dict):
    for model_name in parameters.keys():
        generated_class = DataClassFactory.get_data_class(model_name, parameters)
        globals()[model_name] = generated_class


generate_custom_data_classes(parameters)
