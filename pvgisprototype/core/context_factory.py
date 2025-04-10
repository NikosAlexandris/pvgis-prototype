from rich import print
from pvgisprototype.core.hashing import generate_hash


def parse_fields(
    data_model,
    model_definition,
    fields: list,
) -> dict:
    """ """
    data_container = {}
    print(f"Parsing {fields=} :\n")
    for field in fields:
        print(f"Field : {field}")

        # Get value of field ------------------------------------- <<< Note
        #
        if hasattr(getattr(data_model, field), 'value'):
            field_value = getattr(data_model, field).value
        else:
            field_value = getattr(data_model, field)
        print(f"Value : {field_value}")
        #
        # -----------------------------------------------------------------

        field_title = str()
        if field == "value":
            # If shortname + symbol exist, use'm !
            if hasattr(data_model, "shortname") and hasattr(data_model, "symbol"):
                field_title = f"{data_model.shortname} {data_model.symbol}"

        elif field == "fingerprint":
            print(f"Processing the field {field=}")
            
            field_name = model_definition.get(field, {}).get("title", field)
            print(f"Setting name to {field_name=}")
            
            field_symbol = model_definition.get(field, {}).get("symbol", field)
            print(f"Setting field symbol to {field_symbol=}")
            
            field_title = f"{field_name} {field_symbol}"
            print(f"Setting field title to {field_title=}")

            field_value = generate_hash(data_model.value)
            print(f"Finally, the field value is : {field_value=}")

        else:
            # Get the title for the field from the model definition
            field_title = model_definition.get(field, {}).get("title", field)
        
        print(f"Title : {field_title}")

        # Add to component content with title as key
        data_container[field_title] = field_value
        print(f"[underline]Updated[/underline] field {data_container=}")
        print()

    print(f"[code][underline]Returning[/underline][/code] {data_container=}")
    return data_container


def populate_context(
    self,
    verbose=0,  # required in scope to satisfy conditions set in the YAML files
    fingerprint: bool = True,
):
    """Populate the context of an existing object using YAML definitions"""

    model_name = self.__class__.__name__
    print(f"{model_name=}")

    # model_definition = DataModelFactory.get_model_definition(model_name)
    model_definition = self.model_definition
    print(f"{model_definition=}")

    output = {}
    print(f"{output=}\n")

    # Check if there is a 'presentation' definition in the YAML for that Model
    if "presentation" in model_definition:

        # Get the structure for the presentation
        presentation = model_definition["presentation"]
        print(f"Model data : {presentation}")
        print()

        # Read the structure definitions
        structure = presentation.get("structure")
        print(f"Structure : {structure}")
        print()

        # Iterate the sections, if they exist
        if structure:

            for section_definition in structure:

                section = section_definition.get("section")
                description = section_definition.get("description")
                condition = section_definition.get("condition")
                print(f"[bold]{section=}[/bold]")
                print(f"{description=}")
                print(f"{condition=}")

                output[section] = {}
                print(f"{output=}\n")

                if "subsections" in section_definition:
                    subsection = ""
                    subsections = section_definition.get("subsections")
                    print(f"{subsections=}")

                    subsection_content = {}

                    for subsection_definition in subsections:

                        subsection = subsection_definition.get("subsection")
                        subsection_description = subsection_definition.get(
                            "description"
                        )

                        # output[section][subsection] = {}

                        print(f"[bold]{subsection=}[/bold]")
                        print(f"[bold]{subsection_description=}[/bold]")

                        fields = subsection_definition.get("fields")
                        subsection_content = parse_fields(
                            data_model=self,
                            model_definition=model_definition,
                            fields=fields,
                            # data_container=subsection_content,
                        )

                        output[section][subsection] = subsection_content
                        print(f"{output=}\n")

                else:
                    # Get the parameters
                    fields = section_definition.get("fields")
                    print(f"{fields=}")
                    print()

                    # Check the condition before setting parameters
                    # from devtools import debug
                    # debug(globals())
                    # debug(locals())
                    if condition is None or eval(condition, globals(), locals()):
                        print(f"Condition '{condition}' is met !")
                        print()

                        section_content = {}  # Dictionary for that component

                        # if section == 'Fingerprint':
                        #     print(f"[code]{getattr(target_object, 'value')}[/code]")
                        #     print()
                        #     section_content = generate_hash(getattr(target_object, 'value'))
                        # else:
                        if (
                            fields
                        ):  # Iterate the fields and append them to component content
                            section_content = parse_fields(
                                data_model=self,
                                model_definition=model_definition,
                                fields=fields,
                                # data_container=section_content,
                            )

                        # Append that particular section (Extraterrestrial Irradiance, Metadata, etc)
                        output[section] = section_content
                        print(f"{output=}\n")

    # Feed output to .presentation
    self.presentation = output
