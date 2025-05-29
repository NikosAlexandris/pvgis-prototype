from pvgisprototype.core.hashing import generate_hash
from simpleeval import simple_eval


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
            from rich import print
            print(f"[code][blue]{field=}[/blue][/code]")
            field_name = model_definition.get(field, {}).get("title", field)
            field_symbol = model_definition.get(field, {}).get("symbol", field)
            field_title = f"{field_name} {field_symbol}"
            field_value = generate_hash(data_model.value)
            print(f"[bold]{field_value=}[/bold]")

        else:
            # Get the title for the field from the model definition
            field_title = model_definition.get(field, {}).get("title", field)
        
        # Add to component content with title as key
        data_container[field_title] = field_value

    return data_container

# from rich import print

def populate_context(
    self,
    verbose=0,  
    fingerprint: bool = True,
    locals: dict = {},
):
    """Populate the context of an existing object

    Parameters
    ----------
    self:

    verbose: int
        Verbosity level from the function's local scope. This is required
        compare against the `verbose` condition set in the data model
        definition.

    Notes
    -----
    See also: data model definitions in YAML syntax.

    """

    # from rich import print
    # print()
    # print(f"[bold]Start - Verbose is set to : {verbose=}[/bold]")
    # print()
    # model_name = self.__class__.__name__
    # print(f"> [code]{model_name=}[/code]\n")
    model_definition = self.model_definition
    output = {}

    # Check if there is a 'output' definition in the YAML for that Model
    if "output" in model_definition:

        # Get the structure for the output
        # output = model_definition["output"]

        # Read the structure definitions
        structure = model_definition['output'].get("structure")

        # Iterate the sections, if they exist
        if structure:
            # from rich import print
            # from devtools import debug
            # print(f"{structure=}")
            # print(debug(structure))
            # print()

            for section_definition in structure:
                # print(f"{section_definition=}")
                section = section_definition.get("section")
                # description = section_definition.get("description")
                condition = section_definition.get("condition")
                output[section] = {}
                # print(f"     [code][blue]{section=}[/blue][/code]  if {condition=}")
                # print()

                if "subsections" in section_definition:
                    subsection = ""
                    subsections = section_definition.get("subsections")
                    subsection_content = {}

                    for subsection_definition in subsections:
                        # print(f"   {subsection_definition=}")
                        subsection = subsection_definition.get("subsection")
                        # subsection_description = subsection_definition.get("description")
                        subsection_condition = subsection_definition.get("condition")

                        # print(f"        [code][blue]{subsection=}[/blue][/code]  if {subsection_condition=}")
                        # print()
                        # print(f"{self=}")
                        # print(f"{getattr(self, 'reflectivity', None)=}")

                        # print()
                        # print(f"        [bold]Before [underline]subsection_condition[/underline] evaluation - Verbose is set to : {verbose=}[/bold]")
                        # print()

                        # if subsection_condition is None or getattr(self, subsection_condition, None):#eval(subsection_condition):
                        if subsection_condition is None or simple_eval(subsection_condition, names={'verbose': verbose}):
                            # print(f"           [bold]{subsection_condition=} [green]is met ![/green][/bold]")
                            # print()
                            subsection_content = {}

                            fields = subsection_definition.get("fields")
                            if fields:
                                subsection_content = parse_fields(
                                    data_model=self,
                                    model_definition=model_definition,
                                    fields=fields,
                                )
                            output[section][subsection] = subsection_content
                            # print(f"        [underline bold]Set[/underline bold] [{section=}][{subsection=}]  to  {subsection_content=}")
                            # print()

                        # else:
                            # print(f"        [red][bold]{subsection_condition=} is not met ![/red][/bold]")
                            # print()

                else:

                    # Does the condition evaluate to true ?
                    # print(f"{self=}")
                    # print(f"{self.out_of_range=}")
                    # print(f"{self.out_of_range.size=}")
                    # print()
                    # print(f"[bold]Before condition evaluation - Verbose is set to : {verbose=}[/bold]")
                    # print()
                    if condition is None or simple_eval(condition, names={'verbose': verbose, 'fingerprint': fingerprint}):
                        # print(f"     [bold][code]{condition=}[/code] is met ![/bold]")
                        section_content = {}  # Dictionary for that component

                        fields = section_definition.get("fields")
                        if fields:
                            section_content = parse_fields(
                                data_model=self,
                                model_definition=model_definition,
                                fields=fields,
                            )
                        # print(f"        [underline bold]Set[/underline bold] {section=}  to  {section_content=}")
                        # print()
                        output[section] = section_content
                    # else:
                        # print(f"     [red][code]{condition=} is not met ![/code][/red]")
                        # print()


    # print()
    # print(f"[bold]End-Verbose is set to : {verbose=}[/bold]")
    # print()
    # Feed output to .output
    self.output = output
