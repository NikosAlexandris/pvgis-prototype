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
#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an "AS IS" basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
"""
Dynamic Data Model Initialization

This module generates PVGIS-native data model classes (in fact Pydantic data models)
from centralized definitions and registers them into the global namespace. The generated
models are then exposed at the package level, so applications usually
import them directly from ``pvgisprototype`` rather than from this module.


Architecture
------------
The initialization process follows these steps :

1. Import data model definitions from ``PVGIS_DATA_MODEL_DEFINITIONS``.
2. For each data model definition, ask ``DataModelFactory`` to build the corresponding
   data model class.
3. Register each generated data model class into the module's global namespace
4. Remove the raw definitions to keep the public API clean.

This approach provides several benefits:

- **Centralized Configuration**: All data model schemas defined in one place
- **Dynamic Generation**: Models created at import time from declarative definitions
- **Clean Namespace**: Generated models appear as if directly defined in the module
- **Consistency**: Factory-based approach avoids repetitive boilerplate


Usage
-----
In normal use, models are imported from the top-level package

    >>> from pvgisprototype import SomeDataModel
    >>> instance = SomeDataModel(field_1=value_1, field_2=value_2, ...)

Direct imports from this `__init__` module are typically not required.


Implementation Details
----------------------
- Uses `DataModelFactory.get_data_model()` to construct data model classes
- Modifies `globals()` to register models at module level
- Definitions are deleted after generation to reduce memory footprint


See Also
--------
- pvgisprototype.core.factory.data_model.DataModelFactory : Factory class for
  data model generation
- pvgisprototype.core.data_model.definitions : Central dictionary of data model definitions


Notes
-----
- All model schemas are centrally defined, making them easy to maintain and evolve
- Runtime model customization is possible based on configuration
- Because models are generated dynamically at import time, static analysis tools 
  (IDEs, type checkers) may not recognize them for autocompletion or type checking
- Consider using type stubs (``.pyi`` files) or explicit type annotations for 
  better IDE support and static analysis
"""

from pvgisprototype.core.factory.data_model import DataModelFactory
from pvgisprototype.core.data_model.definitions import PVGIS_DATA_MODEL_DEFINITIONS


def generate_data_models(data_model_definitions: dict):
    """
    Generate and register data model classes from definitions.
    
    Iterates through the provided data model definitions dictionary and
    generates corresponding model classes using the DataModelFactory. Each
    generated data model class is injected into the caller's global namespace,
    making it accessible as a module-level attribute.

    Parameters
    ----------
    data_model_definitions : dict
        Dictionary mapping data model names (str) to their configuration/schema
        definitions. Keys become the class names, values define model structure.
    
    Returns
    -------
    None
        Models are registered as side effects in the global namespace.
    
    Notes
    -----
    This function modifies the global namespace by calling `globals()[name] = model`.
    It should typically only be called once during module initialization.
    
    Examples
    --------
    >>> definitions = {
    ...     'UserModel': {'fields': [...], 'validators': [...]},
    ...     'ProductModel': {'fields': [...], 'validators': [...]}
    ... }
    >>> generate_data_models(definitions)
    >>> # UserModel and ProductModel are now available as module attributes
    """
    for data_model_name in data_model_definitions.keys():
        globals()[data_model_name] = DataModelFactory.get_data_model(
                data_model_name=data_model_name,
                data_model_definitions=data_model_definitions
                )


# Generate data models at module import time
generate_data_models(PVGIS_DATA_MODEL_DEFINITIONS)

# Remove definitions from namespace : prevent external access, reduce footprint ?
del(PVGIS_DATA_MODEL_DEFINITIONS)
