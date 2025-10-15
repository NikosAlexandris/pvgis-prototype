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
import yaml
from copy import deepcopy
from pathlib import Path
from typing import Dict, Any, Set
from pathlib import Path
from typing import Any, Dict, List, Union
from pvgisprototype.core.factory.definition.helpers import extract_structure_from_required, get_structure
from pvgisprototype.core.factory.definition.lists import merge_structure_list
from pvgisprototype.core.factory.definition.load import load_yaml_file
from pvgisprototype.core.factory.definition.merge import deep_merge, merge_dictionaries
from pvgisprototype.core.factory.log import logger


def reorder_output_structure(structure, reference_structure):
    """
    Reorder a merged output structure to match the section order
    from the reference YAML definition.
    - merged_structure: list of dicts (the result of merging)
    - reference_yaml_structure: list of dicts (from top-level output YAML)
    """
    # Map for fast lookup
    merged_map = {section.get("section"): section for section in structure}

    # Only include sections in the order given in the reference YAML
    reordered = [
        merged_map[ref_section.get("section")]
        for ref_section in reference_structure
        if ref_section.get("section") in merged_map
    ]

    # Optional: include any sections not present in reference at the end
    remaining = [
        section for name, section in merged_map.items()
        if name not in [ref_section.get("section") for ref_section in reference_structure]
    ]
    reordered.extend(remaining)

    logger.debug(f"Reordered structure according to YAML: {reference_structure}")

    return reordered


def set_nested_value(
    data: dict,
    path: list,
    value: Any,
    # set_type: bool = False,
    # set_initial: bool = False,
):
    """
    Set a 'value' at a nested dictionary key, creating intermediate dictionaries as needed.
    Ensures 'output' dicts always have 'type' and 'initial' keys.
    """
    if value == [data]:
        logger.debug(
            "Value == [Data] : Safety against self-nesting ! Skipping setting.-"
        )
        return data

    logger.debug(
        f"My job is to set the\n\n{value=}\n\nto\n\n{data=}"
    )
    current = data

    # Traverse to the parent of the final key
    for part in path[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]

    final_key = path[-1]

    if isinstance(current.get(final_key), dict) and isinstance(value, dict):
        logger.debug(
            "Deep merging dictionaries\n\nvalue={value}\n\nand\n\ncurrent[final_key]={current_at_final_key}\n",
            value=value,
            current_at_final_key=current[final_key],
            alt=f"[green]Deep merging dictionaries[/green]\n\n{value=}\n\nand\n\n{current[final_key]=}\n"
        )
        current[final_key] = deep_merge(current[final_key], value)

    else:
        logger.debug(
            f"Setting\n\n{value=}\n\nto\n\n{data=} @ {final_key=}"
        )
        current[final_key] = value

    yaml_dump_of_structure = yaml.dump(data=data, sort_keys=False)
    logger.debug(
        "Updated `data` is"
        + "\n\n{yaml_dump_of_structure}\n",
        yaml_dump_of_structure=yaml_dump_of_structure,
        alt=f"[dim][code]Update data is[/code][/dim]"
        + f"\n\n{yaml_dump_of_structure}\n"
    )


def resolve_requires(
    data: Dict,
    # data: Union[Dict, List, Any],
    source_path: Path,
    resolved_files: Set | None = None,
    cache: Dict[str, Dict] | None = None,
) -> Union[Dict, List, Any]:
    """
    Process a dictionary `data` structure and resolve recursively its `require`
    directives by merging the _current_ data model (also referred to as the
    `child node` or `override`) into the _required_ data (also referred to as
    the `parent node` or `base`).

    The output is a new grand-child node which combines data attributes from a
    child node after inheriting data attributes from the parent node.

    Notes
    -----
    child node : the input `data` structure
    parent node : any `required` directive defined in the input `data` structure

    """
    # logger.debug(
    #     f"Input data for which to resolve require directives is :\n\n {data=}\n"
    # )
    # A cache set to track resolved files and avoide circular dependencies
    if resolved_files is None:
        resolved_files = set()

    # A cache dictionary to store resolved data models (files) by file path
    if cache is None:
        cache = {}

    # Sort of a "base" case : unstructured data need no processing !
    if not isinstance(data, (dict, list)):
        logger.debug(
            "[Unstructured data, needs no processing]",
            alt=f"[dim]\\[Unstructured data, needs no processing][/dim]",
        )
        return data 

    if isinstance(data, dict):

        # Detect an already resolved path to avoid circular dependencies
        current_file_path = data.get('_file_path', None)
        if current_file_path:
            if current_file_path in resolved_files:
                logger.warning(
                    "Detected a circular dependency : file path {current_file_path} already resolved ! Skipping.-",
                    current_file_path=current_file_path,
                    alt=f"Detected a circular dependency : file path {current_file_path} already resolved ! Skipping.-",
                )
                return data  # Skip circular dependencies

            # Tracking the file path
            logger.info(
                "Tracking the file path {current_file_path}",
                current_file_path=current_file_path,
                alt=f"[yellow]Tracking the file path[/yellow] {current_file_path}",
            )
            resolved_files.add(current_file_path)
            cache[current_file_path] = data  # Cache current state

        # Deep copy to avoid mutation during iteration
        data = deepcopy(data)

        # Process top-level `require` directive
        if 'require' in data:

            # Handle missing 'name' key
            data_model_name = data.get('name', '<unnamed data model>')
            logger.debug(
                f"Identified require directives in `{data_model_name}`"
            )

            requires = data.pop("require")
            # The `require` directive may or may not list multiple items ?
            # If a single "item" (string?), make it a list
            requires_list = [requires] if not isinstance(requires, list) else requires
            require_directives = "- " + "\n   - ".join(requires_list)

            logger.debug(
                "   Parents for {data_model_name}\n\n   {require_directives}\n",
                data_model_name=data_model_name,
                require_directives=require_directives,
                alt=f"[dim]   Parents for [/dim][bold]{data_model_name}[/bold]\n\n   [yellow]{require_directives}[/yellow]\n",
            )
            if len(require_directives) > 0:
                logger.debug(
                    "   >>> Integrating required items >>> >>> >>>\n",
                    alt=f"   [dim]>>> Integrating required items >>> >>> >>>[/dim]\n",
                )

            merged_structure = []

            # Resolve recursively, merge sequentially via `reverse()` :
            # respect order so a later require can override an earlier one
            # for required_item in reversed(requires):
            for required_item in requires:  # Don't touch me ! Unless you really know what you are doing !

                #
                # Load and cache data model
                #

                # First, build the path to the require YAML file
                required_path = (source_path / required_item).with_suffix('.yaml')
                # required_path.is_file()

                # Next check if the file is already processed, thus cached
                if str(required_path) in cache:
                    logger.debug(
                        "Using cached parent data model definition\n\n{required_path}",
                        required_path=required_path,
                        alt=f"Using cached parent data model definition\n\n{required_path}"
                    )
                    required_data = cache[str(required_path)]

                else:
                    required_data = load_yaml_file(required_path)
                    logger.info(
                            f"Required data model\n\n{required_data=}\n"
                            )

                    if isinstance(required_data, dict):
                        required_data['_file_path'] = str(required_path)
                        logger.debug(
                            "Caching {required_path}",
                            required_path=required_path,
                            alt=f"[magenta]Caching {required_path}[/magenta]",
                        )
                        cache[str(required_path)] = required_data
                    else:
                        logger.warning(
                            "Cannot track required parent data model node\n\n{required_data}\n\nis a list !\n",
                            required_data=required_data,
                            alt=f"[bold]Cannot track[/bold] required parent data model node\n\n{required_data}\n\nis a list !\n",
                        )

                #
                # Resolve require directives
                #

                try:
                    # Recursively resolve base model
                    required_data = resolve_requires(
                        data=required_data, 
                        source_path=source_path,
                        resolved_files=resolved_files.copy(),
                        cache=cache,
                    )
                except Exception as exception:
                    logger.error(
                        "Failed to resolve required `parent` YAML data model definition :\n\n File path : {required_path}\n\nData : {required_data}\n\nSource path : {source_path}\n\nResolved files : {resolved_files}\n\nCache : {cache}\n\nError : {exception}",
                        required_path=required_path,
                        required_data=required_data,
                        source_path=source_path,
                        resolved_files=resolved_files,
                        cache=cache,
                        exception=exception,
                        alt=f"Failed to resolve required `parent` YAML file : {required_path}\n\n{required_data}\n\n{source_path}\n\n{resolved_files}\n\n{cache}\n\nError : {exception}",
                    )
                    # continue
                    raise ValueError(f"Error resolving YAML file {required_data}")

                #
                # Process output-structure from required_data if present
                #

                ## Extract the base output-structure (list) : parent node output structure

                base_structure = extract_structure_from_required(
                    required_data=required_data
                )

                if base_structure:

                    merged_structure = merge_structure_list(
                        # base_structure=merged_structure,
                        # override_structure=base_structure,
                        base_structure=base_structure,
                        override_structure=merged_structure,
                    )

                    ## Then get the child node output structure
                    structure_list = get_structure(data=data)
                    if structure_list:
                        merged_structure = merge_structure_list(
                            base_structure=merged_structure,
                            override_structure=structure_list,
                        )
                    logger.debug(f"Before inheriting from parent output structure, data is\n\n   {data=}")
                    # --------------------------------------------------------
                    if len(base_structure) == 1:
                        logger.debug(f"Base structure lists a single item\n\n   {data=}")
                        base_node = base_structure[0]
                        base_node.update(data)
                        data = base_node

                    # else:
                    #     set_nested_value(
                    #         data,
                    #         ["sections", "output", "structure"],
                    #         merged_structure,
                    #     )

                    # --------------------------------------------------------
                    # for parent_node in base_structure:
                    #     parent_node.update(data)
                    # --------------------------------------------------------

                    yaml_dump_of_structure = yaml.dump(data=data, sort_keys=False)
                    logger.debug(
                        "{data_model_name} after inheriting is"
                        + "\n\n{yaml_dump_of_structure}\n",
                        data_model_name=data_model_name,
                        yaml_dump_of_structure=yaml_dump_of_structure,
                        alt=f"   [dim][code]{data_model_name}[/code] after inheriting is[/dim]"
                        + f"\n\n   [dim]{yaml_dump_of_structure}[/dim]\n"
                    )

                else:
                    # Merge (non-output-structure templates) required_data (base) into current data (override)
                    # or else said : the "current" data['name']  overrides  the "base" required_data['name']
                    logger.debug(
                        f"No parent output structure found!"
                        +" Deep-merge non-output-structure dictionaries/lists templates!"
                    )
                    data = deep_merge(
                        base=required_data,
                        override=data,
                    )
                    yaml_dump_of_structure = yaml.dump(data=data, sort_keys=False)
                    logger.debug(
                        "{data_model_name} after deep-merging is"
                        + "\n\n{yaml_dump_of_structure}\n",
                        data_model_name=data_model_name,
                        yaml_dump_of_structure=yaml_dump_of_structure,
                        alt=f"   [dim][code]{data_model_name}[/code] after deep-merging is[/dim]"
                        + f"\n\n   [dim]{yaml_dump_of_structure}[/dim]\n"
                    )

            # Apply accumulated structure
            if merged_structure:
                logger.debug(
                    "More merging... !"
                )
                existing_structure = get_structure(data)
                final_structure = merge_structure_list(
                    existing_structure,
                    merged_structure, 
                )
                structure_list = get_structure(data=data)
                # # Reorder output ?
                # final_structure = reorder_output_structure(
                #     structure=final_structure,
                #     reference_structure=structure_list,
                # )
                set_nested_value(data, ["sections", "output", "structure"], final_structure)

        # Recurse into nested keys
        # logger.info(
        #     "The data structure\n\n{data}\n\ndoes not contain any `require` directives. Recurse into nested keys.",
        #     data=data,
        #     alt=f"The data structure\n\n{data}\n\ndoes not contain any `require` directives. Recurse into nested keys.",
        # )
        logger.info(
            "Recurse into nested data keys\n\n{data_keys}\n",
            data_keys=data.keys(),
            alt=f"Recurse into nested data keys\n\n{data.keys()=}\n",
        )
        for key, value in data.items():
            logger.info(
                "Resolve `{key}`",
                key=key,
                alt=f"Resolve {key=}",
            )
            data[key] = resolve_requires(
                data=value,
                source_path=source_path,
                resolved_files=resolved_files.copy(),
                cache=cache,
            )
        yaml_dump_of_structure = yaml.dump(data=data, sort_keys=False)
        logger.debug(
            "Resolved data is"
            + "\n\n{yaml_dump_of_structure}\n",
            yaml_dump_of_structure=yaml_dump_of_structure,
            alt=f"[dim][code]Resolved data is[/code][/dim]"
            + f"\n\n{yaml_dump_of_structure}\n"
        )

        return data

    elif isinstance(data, list):
        # Recurse into each item in the list
        # for i, item in enumerate(data):
        #     data[i] = resolve_requires(item, source_path)
        return [
            resolve_requires(
                data=item,
                source_path=source_path,
                resolved_files=resolved_files.copy(),
                cache=cache,
            )
            for item in reversed(data)  # Don't touch me ! Unless you really know what you are doing !
        ]

    # if 'name' in data:
    #     data_model_name = data['name']
    #     logger.debug(
    #             "    Resolved {data_model_name} is\n\n   {data}\n",
    #             data_model_name=data_model_name,
    #             data=data,
    #             alt=f"    [code]Resolved[/code] {data_model_name} is\n\n   {yaml.dump(data, sort_keys=False)}\n",
    #     )

    # else:

    #     return data
