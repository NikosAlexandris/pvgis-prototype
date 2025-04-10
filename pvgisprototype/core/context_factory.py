from pvgisprototype.core.hashing import generate_hash


def parse_fields(
    data_model,
    model_definition,
    fields: list,
) -> dict:
    """ """
    data_container = {}
    for field in fields:

        # Get value of field ------------------------------------- <<< Note
        #
        if hasattr(getattr(data_model, field), 'value'):
            field_value = getattr(data_model, field).value
        else:
            field_value = getattr(data_model, field)
        #
        # -----------------------------------------------------------------

        field_title = str()
        if field == "value":
            # If shortname + symbol exist, use'm !
            if hasattr(data_model, "shortname") and hasattr(data_model, "symbol"):
                field_title = f"{data_model.shortname} {data_model.symbol}"

        elif field == "fingerprint":
            field_name = model_definition.get(field, {}).get("title", field)
            field_symbol = model_definition.get(field, {}).get("symbol", field)
            field_title = f"{field_name} {field_symbol}"
            field_value = generate_hash(data_model.value)
        else:
            # Get the title for the field from the model definition
            field_title = model_definition.get(field, {}).get("title", field)
        
        # Add to component content with title as key
        data_container[field_title] = field_value

    return data_container


def populate_context(
    self,
    verbose=0,  # required in scope to satisfy conditions set in the YAML files
    fingerprint: bool = True,
):
    """Populate the context of an existing object using YAML definitions"""

    model_name = self.__class__.__name__
    model_definition = self.model_definition
    output = {}

    # Check if there is a 'presentation' definition in the YAML for that Model
    if "presentation" in model_definition:

        # Get the structure for the presentation
        presentation = model_definition["presentation"]

        # Read the structure definitions
        structure = presentation.get("structure")

        # Iterate the sections, if they exist
        if structure:
            for section_definition in structure:
                section = section_definition.get("section")
                description = section_definition.get("description")
                condition = section_definition.get("condition")
                output[section] = {}

                if "subsections" in section_definition:
                    subsection = ""
                    subsections = section_definition.get("subsections")
                    subsection_content = {}

                    for subsection_definition in subsections:
                        subsection = subsection_definition.get("subsection")
                        subsection_description = subsection_definition.get(
                            "description"
                        )
                        fields = subsection_definition.get("fields")
                        subsection_content = parse_fields(
                            data_model=self,
                            model_definition=model_definition,
                            fields=fields,
                        )

                        output[section][subsection] = subsection_content

                else:
                    # Get the parameters
                    fields = section_definition.get("fields")

                    # Check the condition before setting parameters
                    if condition is None or eval(condition, globals(), locals()):
                        section_content = {}  # Dictionary for that component
                        if (
                            fields
                        ):  # Iterate the fields and append them to component content
                            section_content = parse_fields(
                                data_model=self,
                                model_definition=model_definition,
                                fields=fields,
                            )

                        # Append that particular section (Extraterrestrial Irradiance, Metadata, etc)
                        output[section] = section_content

    # Feed output to .presentation
    self.presentation = output
