from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, Set
from copy import deepcopy
import yaml
from pathlib import Path
from typing import Any, Dict, List, Union
from pvgisprototype.core.factory.definition.merge import merge_dictionaries
from pvgisprototype.core.factory.log import logger


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """
    Load a data model definition from a properly structured YAML file into a
    Python dictionary.
    """
    try:
        logger.debug(
            f"Loading {file_path}...",
            alt=f"Loading [bold]{file_path.as_posix()}[/bold]"
            )
        with open(file_path, "r") as yaml_file:
            return yaml.safe_load(yaml_file)
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")

    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {file_path}: {e}")


def log_data_model_loading(
        data_model,
        data_model_name,
        require: bool = False,
        ):
    """
    """
    if not require:
        logger.debug(
            f"Processing data model {data_model_name}",
            alt=f"[dim]Processing data model [code]{data_model_name}[/code] :[/dim]\n\n{yaml.dump(data_model, sort_keys=False)}",
        )
    else:
        logger.debug(
             "Require data model :\n{yaml.dump(data_model, default_flow_style=False, sort_keys=False,)}",
             data_model=data_model,
             alt=f"Require data model :\n[bold]{yaml.dump(data_model, default_flow_style=False, sort_keys=False,)}[/bold]"
        )


def merge_structure_list(
    base_structure: List[Dict],
    override_structure: List[Dict]
) -> List[Dict]:
    """
    Merge two structure lists by section.
    If a section exists in both, merge subsections by 'subsection' key.
    If only in base, add to override.
    """
    merged = deepcopy(override_structure)

    for base_item in base_structure:
        base_section = base_item.get('section')
        base_subsections = base_item.get('subsections', [])

        match_found = False
        for i, override_item in enumerate(merged):
            override_section = override_item.get('section')

            # Match by section name
            if base_section == override_section:
                # Merge subsections
                override_subsections = override_item.get('subsections', [])
                override_subsection_map = {
                    sub.get('subsection'): sub for sub in override_subsections
                }

                # Merge base subsections into override
                for base_sub in base_subsections:
                    sub_key = base_sub.get('subsection')
                    if sub_key in override_subsection_map:
                        # Merge fields instead of replacing
                        override_sub = override_subsection_map[sub_key]
                        base_sub_fields = base_sub.get("fields", [])
                        override_sub_fields = override_sub.get("fields", [])

                        merged_fields = list({
                            f for f in base_sub_fields + override_sub_fields
                        })  # Deduplicate fields

                        # Preserve override fields + add base fields
                        override_sub["fields"] = merged_fields

                    else:
                        # Add new subsection
                        override_subsection_map[sub_key] = base_sub

                merged[i]['subsections'] = list(override_subsection_map.values())
                match_found = True
                break

        if not match_found:
            # No matching section in override, append base item
            merged.append(deepcopy(base_item))

    logger.debug(
        "   + Merged-in output structure is\n\n {merged}\n",
        merged=merged,
        alt=f"   + [bold magenta]Merged-in output structure is[/bold magenta]\n\n   [magenta]{merged}[/magenta]\n",
    )

    return merged


def find_structure_in_path(data: Dict, path: List[str]) -> Union[List, None]:
    """Navigate nested dict to find structure at specified path."""
    data_model_name = data['name']
    for part in path:
        if isinstance(data, dict) and part in data:
            data = data[part]
            logger.debug(
                "   Output structure in {data_model_name} [Child]\n\n   {data}\n",
                data_model_name=data_model_name,
                data=data,
                alt=f"   [dim bold]Override output structure[/dim bold] in {data_model_name} [Child]\n\n   [dim]{data}[/dim]\n",
            )

        else:
            return None

    return data if isinstance(data, list) else None


def extract_structure_from_required(required_data: dict) -> List[dict]:
    """
    Extract the output structure list from the required file at
    `sections.output.structure`.
    """
    structure = []
    if 'sections' in required_data:
        output = required_data['sections'].get('output', {})
        if output:
            logger.debug(
                    f"   ! Identified an `output` structure !\n",
                    alt=f"   ! [blue bold]Identified an `output` structure ![/blue bold]\n",
                    )
        if 'structure' in output:
            structure = output['structure']
            required_data_model_name = required_data['name']
            yaml_dump_of_structure = yaml.dump(data=structure, sort_keys=False)
            logger.debug(
                "   Base output structure"
                + "in {required_data_model_name} :"
                + "\n\n   {yaml_dump_of_structure}\n",
                required_data_model_name=required_data_model_name,
                yaml_dump_of_structure=yaml_dump_of_structure,
                structure=structure,
                alt=f"   [dim][bold]Base[/bold] output structure[/dim]"
                + f"in {required_data_model_name} :"
                + f"\n\n   [dim]{yaml_dump_of_structure}[/dim]\n"
            )
    return structure


def set_nested_value(
    data: Dict,
    path: List[str],
    value: Any,
):
    """
    Set a "value" at a nested dictionary key.
    """
    for part in path[:-1]:
        if part == 'output':
            data = data.setdefault(part, {'type': 'dict', 'initial': {}})
        else:
            data = data.setdefault(part, {})

    # Preserve existing keys in the target dictionary if it already exists
    if isinstance(data.get(path[-1]), dict) and isinstance(value, dict):
        data[path[-1]].update(value)
    else:
        data[path[-1]] = value

    logger.debug(
        "   = Consolidated data model output structure is\n\n   {data}\n",
        data=data,
        alt=f"   = [bold magenta]Consolidated data model output structure is[/bold magenta]\n\n   [magenta]{data}[/magenta]\n",
    )



@lru_cache(maxsize=128)
def cached_resolve_require_directives(
    required_path: str,
    source_path: str
) -> Dict[str, Any]:
    """
    """
    required_path = Path(required_path)
    source_path = Path(source_path)

    required_data = load_yaml_file(required_path)
    required_data['_required_path'] = str(required_path)  # Track file path for circular dep detection
    resolved_data = resolve_requires(
        data=required_data,
        source_path=source_path,
    )

    return resolved_data


def resolve_requires(
    data: Dict,
    # data: Union[Dict, List, Any],
    source_path: Path,
    resolved_files: Set | None = None,
    cache: Dict[str, Dict] | None = None,
) -> Union[Dict, List, Any]:
    """
    Recursively process `require` directives in a data structure and merge the
    _current_ data (also referred to as the `override`) into the _required_
    data (also referred to as the `base`).
    """
    # A cache set to track resolved files and avoide circular dependencies
    if resolved_files is None:
        resolved_files = set()

    # A cache dictionary to store resolved data models (files) by file path
    if cache is None:
        cache = {}

    # Sort of a "base" case
    if not isinstance(data, (dict, list)):
        return data  # Unstructured data need no processing

    if isinstance(data, dict):

        # Detect an already resolved path to avoid circular dependencies
        file_path = data.get('_file_path')
        if file_path:
            if file_path in resolved_files:
                logger.warning(f"Detected a circular dependency. Skipping : {file_path}")
                return data  # Skip circular dependencies

            # Tracking the resolved path
            resolved_files.add(file_path)
            cache[file_path] = data  # Cache current state

        # Process top-level `require` directive
        if 'require' in data:
            requires = data.pop("require")

            # The `require` directive may or may not list multiple items ?
            # If a single "item" (string?), make it a list
            requires_list = [requires] if not isinstance(requires, list) else requires
            require_directives = "- " + "\n   - ".join(requires_list)
            data_model_name = data['name']
            logger.debug(
                "   Parents for {data_model_name}\n\n   {require_directives}\n",
                data_model_name=data_model_name,
                require_directives=require_directives,
                alt=f"[dim]   Parents for [/dim][bold]{data_model_name}[/bold]\n\n   [yellow]{require_directives}[/yellow]\n",
            )
            if len(require_directives) > 1:
                logger.debug(
                    "   >>> Integrating required items >>> >>> >>>\n",
                    alt=f"   [dim]>>> Integrating required items >>> >>> >>>[/dim]\n",
                    )

            # ======================================================================================
            # Caching ?
            # # Loop over the list
            # for required_item in requires:
            #     required_path = (source_path / required_item).with_suffix('.yaml')
            #     # required_data_structure = load_yaml_file(required_path)
            #     required_data = cached_resolve_require_directives(
            #             required_path=str(required_path),
            #             source_path=str(source_path),
            #     )  # Recurse
            # ======================================================================================

            # Resolve recursively, merge sequentially via `reverse()` :
            # respect order so a later require can override an earlier one
            for required_item in reversed(requires):

                # First, build the path to the require YAML file
                required_path = (source_path / required_item).with_suffix('.yaml')

                # Next check if the file is already processed, thus cached
                if str(required_path) in cache:
                    logger.debug(f"Using cached {required_path}")
                    required_data = cache[str(required_path)]

                else:
                    required_data = load_yaml_file(required_path)
                    logger.debug(
                        "",
                        alt=f"[magenta]Track {required_path}[/magenta]",
                    )
                    required_data['_file_path'] = str(required_path)

                try:
                    # Recursively resolve base model
                    required_data = resolve_requires(
                        data=required_data, 
                        source_path=source_path,
                        resolved_files=resolved_files.copy(),
                        cache=cache,
                    )
                except Exception as e:
                    logger.warning(
                            f"Failed to resolve required `base` YAML file : {required_path} - {e}",
                            alt=f"Failed to resolve required `base` YAML file : {required_path} - {e}",
                            )
                    continue

                # Process output-structure from required_data if present

                # Extract the base output-structure (list)
                base_structure = extract_structure_from_required(
                    required_data=required_data
                )
                structure_list = find_structure_in_path(
                    data=data, path=["sections", "output", "structure"]
                )
                if base_structure and structure_list:
                        # Merge the _current_ output-structure-list into the _base_ output-structure
                    merged_structure = merge_structure_list(
                        base_structure=base_structure,
                        override_structure=structure_list,
                    )
                    set_nested_value(
                        data=data,
                        path=["sections", "output", "structure"],
                        value=merged_structure,
                    )
                elif base_structure:
                    set_nested_value(
                        data=data,
                        path=["sections", "output", "structure"],
                        value=base_structure,
                    )
                else:
                    # Merge (non-output-structure templates) required_data (base) into current data (override)
                    # or else said : the "current" data['name']  overrides  the "base" required_data['name']
                    data = merge_dictionaries(
                        base=required_data,
                        override=data,
                    )

        # Recurse into nested keys
        for key, value in data.items():
            data[key] = resolve_requires(
                data=value,
                source_path=source_path,
                resolved_files=resolved_files.copy(),
                cache=cache,
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
            for item in data
        ]

    # if 'name' in data:
    #     data_model_name = data['name']
    #     logger.debug(
    #             "    Resolved {data_model_name} is\n\n   {data}\n",
    #             data_model_name=data_model_name,
    #             data=data,
    #             alt=f"    [code]Resolved[/code] {data_model_name} is\n\n   {yaml.dump(data, sort_keys=False)}\n",
    #     )
    else:

        return data


def load_data_model(
    source_path: Path,
    data_model_yaml: Path,
    require: bool = False,
) -> Dict[str, Any]:
    """
    Load and consolidate a YAML data model definition and return a nested
    dictionary compatible with `DataModelFactory`.
    """
    # Load data model description
    data_model = load_yaml_file(data_model_yaml)
    data_model_name = data_model["name"]
    log_data_model_loading(
        data_model=data_model,
        data_model_name=data_model_name,
        require=require,
    )

    # Resolve requirements
    data_model = resolve_requires(
            data=data_model,
            source_path=source_path,
            )
    # del(data_model['sections']['_file_path'])  # sane post-processing ?

    # logger.info(
    #     "Return consolidated data model :\n" + yaml.dump(data={data_model_name: data_model['sections']}, default_flow_style=False, sort_keys=False),
    #     alt="[dim]Return consolidated data model :[/dim]\n" + yaml.dump(data={data_model_name: data_model['sections']}, default_flow_style=False, sort_keys=False),
    # )

    return {data_model_name: data_model.get('sections', {})}
    # return {data_model_name: data_model['sections']}  # Old !
