from pvgisprototype.core.data_class_factory import DataClassFactory
from pvgisprototype.core.classes.pvis_data_classes_definitions import pvis_data_classes


def generate_custom_data_classes(definitions: dict):
    for class_name in definitions.keys():
        generated_class = DataClassFactory.get_data_class(class_name, definitions)
        globals()[class_name] = generated_class


generate_custom_data_classes(pvis_data_classes)
