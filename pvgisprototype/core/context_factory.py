from collections import defaultdict
from pvgisprototype.core.data_model_factory import DataModelFactory
from pvgisprototype.core.data_model_definitions import PVGIS_DATA_MODEL_DEFINITIONS
from rich import print


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

    def _parse_fields(self, data_model, model_definition, fields: list, data_container: dict) -> dict:
        """
        """
        print(f"Parsing {fields=} :\n")
        for field in fields:
            print(f"Field : {field}")

            # Get value of field
            field_value = getattr(data_model, field)
            print(f"Value : {field_value}")

            field_title = str()
            if field == 'value':
                if hasattr(data_model, 'shortname') and hasattr(data_model, 'symbol'):
                    field_shortname = getattr(data_model, 'shortname')
                    field_symbol = getattr(data_model, 'symbol')
                    field_title = f"{field_shortname} {field_symbol}"
            else:
                # Get the title for the field from the model definition
                field_title = model_definition.get(field, {}).get('title', field)
            print(f"Title : {field_title}")

            # Add to component content with title as key
            data_container[field_title] = field_value
            print(f"[underline]Updated[/underline] {data_container=}")
            print()

        return data_container

    def populate_context(self, target_object, verbose=0, fingerprint=False):
        """Populate the context of an existing object using YAML definitions"""

        model_name = target_object.__class__.__name__
        print(f"{model_name=}")

        model_definition = DataModelFactory.get_model_definition(model_name)
        print(f"{model_definition=}")

        output = {}
        print(f"{output=}\n")

        # Check if there is a 'presentation' definition in the YAML for that Model
        if 'presentation' in model_definition:
            
            # Get the structure for the presentation
            presentation = model_definition['presentation']
            print(f'Model data : {presentation}')
            print()

            # Read the structure definitions
            structure = presentation.get('structure')
            print(f"Structure : {structure}")
            print()

            # Iterate the sections, if they exist
            if structure:

                for section_definition in structure:

                    section = section_definition.get('section')
                    description = section_definition.get('description')
                    condition = section_definition.get('condition')
                    print(f"[bold]{section=}[/bold]")
                    print(f"{description=}")
                    print(f"{condition=}")

                    output[section] = {}
                    print(f"{output=}\n")

                    if 'subsections' in section_definition:
                        subsection = ''
                        subsections = section_definition.get('subsections')
                        print(f"{subsections=}")

                        subsection_content = {}
                        
                        for subsection_definition in subsections:

                            subsection = subsection_definition.get('subsection')
                            subsection_description = subsection_definition.get('description')

                            # output[section][subsection] = {}
                            
                            print(f"[bold]{subsection=}[/bold]")
                            print(f"[bold]{subsection_description=}[/bold]")
                            
                            fields = subsection_definition.get('fields')
                            subsection_content = self._parse_fields(
                                    data_model=target_object,
                                    model_definition=model_definition,
                                    fields=fields,
                                    data_container=subsection_content,
                                    )

                            output[section][subsection] = subsection_content
                            print(f"{output=}\n")

                    else:
                        # Get the parameters
                        fields = section_definition.get('fields')
                        print(f"{fields=}")
                        print()

                        # Check the condition before setting parameters
                        if condition is None or eval(condition, globals(), locals()):
                            print(f"Condition '{condition}' is met !")
                            print()

                            section_content = {}  # Dictionary for that component

                            if section == 'Fingerprint':
                                section_content = generate_hash(getattr(target_object, 'value'))

                            else:
                                if fields:  # Iterate the fields and append them to component content
                                    section_content = self._parse_fields(
                                            data_model=target_object,
                                            model_definition=model_definition,
                                            fields=fields,
                                            data_container=section_content,
                                            )

                            # Append that particular section (Extraterrestrial Irradiance, Metadata, etc)
                            output[section] = section_content
                            print(f"{output=}\n")


        # Set the 'presentation' to your object
        target_object.presentation = output
