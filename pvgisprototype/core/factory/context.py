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
from pvgisprototype.core.hashing import generate_hash
from simpleeval import simple_eval
from collections import OrderedDict
from numpy import array as numpy_array


def parse_fields(
    data_model,
    model_definition,
    fields: list,
) -> dict:
    """
    Notes
    -----
    The _output_ field title (or name) is composed by the `shortname` and the
    `symbol`, both defined in the YAML-based definition of a data model.

    """
    data_container = OrderedDict()
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
                # field_title = f"{data_model.shortname}"

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
    model_definition = self.model_definition
    output = OrderedDict()

    # Check if there is an 'output' definition in the YAML for that Model
    if "output" in model_definition:

        # Read the structure definitions
        structure = model_definition['output'].get("structure")

        # Iterate the sections, if they exist
        if structure:

            for section_definition in structure:
                section = section_definition.get("section")
                condition = section_definition.get("condition")
                output[section] = {}

                if "subsections" in section_definition:
                    subsection = ""
                    subsections = section_definition.get("subsections")
                    subsection_content = {}

                    for subsection_definition in subsections:
                        subsection = subsection_definition.get("subsection")
                        subsection_condition = subsection_definition.get("condition")

                        # Build a `names` dictionary dynamically 
                        names = {
                            'verbose': verbose,
                            'reflectivity_factor': getattr(self, 'reflectivity_factor', numpy_array([])),
                            # other attributes ?
                        }
                        
                        if subsection_condition is None or simple_eval(
                            subsection_condition,
                            names=names,
                        ):
                            subsection_content = {}

                            fields = subsection_definition.get("fields")
                            if fields:
                                subsection_content = parse_fields(
                                    data_model=self,
                                    model_definition=model_definition,
                                    fields=fields,
                                )
                            output[section][subsection] = subsection_content

                else:

                    # Build names dictionary - include self so conditions can access attributes
                    names = {
                        "verbose": verbose,
                        "fingerprint": fingerprint,
                        "out_of_range": getattr(self, "out_of_range", numpy_array([])),
                    }

                    # Does the condition evaluate to true ?
                    if condition is None or simple_eval(
                        condition,
                        names=names,
                    ):
                        section_content = {}  # Dictionary for that component

                        fields = section_definition.get("fields")
                        if fields:
                            section_content = parse_fields(
                                data_model=self,
                                model_definition=model_definition,
                                fields=fields,
                            )
                        output[section] = section_content


    # Feed output to .output
    self.output = output
