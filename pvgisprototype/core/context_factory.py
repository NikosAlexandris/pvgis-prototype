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
from collections import defaultdict
from pvgisprototype.core.data_model_factory import DataModelFactory
from pvgisprototype.core.data_model_definitions import PVGIS_DATA_MODEL_DEFINITIONS

#def generate_hash(data): # Added this, to avoid the 'name not defined' issue
#    return hash(data.tobytes())

#class ContextBuilder:
#    def __init__(self):
#        self._dependency_graph = self._build_dependency_graph()

#    def _build_dependency_graph(self):
#        graph = defaultdict(set)
#        for model_name in PVGIS_DATA_MODEL_DEFINITIONS:
#            model_def = DataModelFactory.get_model_definition(model_name)
#            for component in model_def.get('context_components', []):
#                graph[model_name].add(component)
#        return graph

#    def populate_context(self, target_object, verbose=0, fingerprint=False):
#        """Populate the context of an existing object using YAML definitions"""
#        model_name = target_object.__class__.__name__
#        model_def = DataModelFactory.get_model_definition(model_name)

#        components = {}

#        # Check if there is a 'components' definition in the YAML for that Model
#        if 'components' in model_def:
#            # Get model data
#            model_data = model_def['components']
#            # Read the structure definitions
#            structure = model_data.get('structure')
#            # Iterate the sections, if they exist
#            if structure:
#                for section_def in structure:
#                    # Get the parameters
#                    section = section_def.get('section')
#                    fields = section_def.get('fields')
#                    condition = section_def.get('condition')

#                    #Check the condition before setting parameters
#                    if condition is None or eval(condition, globals(), locals()):
#                        component_content = {} # Dictionary for that component
#                        if fields: # Iterate the fields and append them to component content
#                            for field in fields:
#                       # Get the field value
#                                field_value = getattr(target_object, field)

#                                # Get the title for the field from the model definition
#                                field_title = model_def.get(field, {}).get('title', field)

#                                # Add to component content with title as key
#                                component_content[field_title] = field_value

#                        #Append that particular section (Extraterrestrial Irradiance, Metadata, etc
#                        components[section] = component_content
#                        # components[field] = component_content

#        # Set the components to your object
#        target_object.components = components



#from collections import defaultdict
#from pvgisprototype.core.data_model_factory import DataModelFactory
#from pvgisprototype.core.data_model_definitions import PVGIS_DATA_MODEL_DEFINITIONS

def generate_hash(data):  # Added this, to avoid the 'name not defined' issue
    return hash(data.tobytes())

class ContextBuilder:
    def __init__(self):
        self._dependency_graph = self._build_dependency_graph()

    def _build_dependency_graph(self):
        graph = defaultdict(set)
        for model_name in PVGIS_DATA_MODEL_DEFINITIONS:
            model_definition = DataModelFactory.get_model_definition(model_name)
            for component in model_definition.get('dependencies', []):
                graph[model_name].add(component)

        print(f"{graph=}")
        return graph

    def populate_context(self, target_object, verbose=0, fingerprint=False):
        """Populate the context of an existing object using YAML definitions"""
        model_name = target_object.__class__.__name__
        print(f"{model_name=}")
        model_definition = DataModelFactory.get_model_definition(model_name)
        print(f"{model_definition=}")

        components = {}

        # Check if there is a 'components' definition in the YAML for that Model
        if 'components' in model_definition:
            
            # Get the structure for the components
            components = model_definition['components']
            print(f'Model data : {components}')
            print()

            # Read the structure definitions
            structure = components.get('structure')
            print(f"Structure : {structure}")
            print()

            # Iterate the sections, if they exist
            if structure:
                for section_definition in structure:

                    # print('-------------------------------------')
                    # print(f"Section def : {section_def}")
                    # print()

                    # Get the parameters
                    section = section_definition.get('section')
                    fields = section_definition.get('fields')
                    condition = section_definition.get('condition')

                    print(f"Section : {section}")
                    print(f"Fields : {fields}")
                    print(f"Condition : {condition}")
                    print()

                    # Check the condition before setting parameters
                    if condition is None or eval(condition, globals(), locals()):
                        print(f"Condition is : {condition}")
                        print()
                        component_content = {}  # Dictionary for that component
                        if section == 'Fingerprint':
                            component_content = generate_hash(getattr(target_object, 'value'))
                        else:
                            if fields:  # Iterate the fields and append them to component content
                                for field in fields:
                                    print(f"Field : {field}")

                                    # Get the field value
                                    field_value = getattr(target_object, field)
                                    print(f"Value : {field_value}")

                                    field_title = str()
                                    if field == 'value':
                                        if hasattr(target_object, 'shortname') and hasattr(target_object, 'symbol'):
                                            field_shortname = getattr(target_object, 'shortname')
                                            field_symbol = getattr(target_object, 'symbol')
                                            field_title = f"{field_shortname} {field_symbol}"
                                    else:
                                        # Get the title for the field from the model definition
                                        field_title = model_definition.get(field, {}).get('title', field)
                                    print(f"Title : {field_title}")

                                    # Add to component content with title as key
                                    component_content[field_title] = field_value
                                    # print(f"Component content : {component_content}")
                                    # print()

                        # Append that particular section (Extraterrestrial Irradiance, Metadata, etc)
                        components[section] = component_content

        # Set the 'components' to your object
        target_object.components = components
