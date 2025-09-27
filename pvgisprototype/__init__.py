#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
from pvgisprototype.core.factory.data_model import DataModelFactory
from pvgisprototype.core.data_model.definitions import PVGIS_DATA_MODEL_DEFINITIONS


def generate_data_models(data_model_definitions: dict):
    for data_model_name in data_model_definitions.keys():
        globals()[data_model_name] = DataModelFactory.get_data_model(
                data_model_name=data_model_name,
                data_model_definitions=data_model_definitions
                )


generate_data_models(PVGIS_DATA_MODEL_DEFINITIONS)
del(PVGIS_DATA_MODEL_DEFINITIONS)
