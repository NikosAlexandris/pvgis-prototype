import yaml
from typing import Dict, Any, List
from pathlib import Path
from rich import print
from rich.progress import track
from rich.table import Table
from rich.console import Console


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """
    Load a YAML file and return its contents as a dictionary.

    Parameters
    ----------
    file_path : str
        Path to the YAML file.

    Returns
    -------
    dict
        Parsed YAML content as a dictionary.
    """
    try:
        with open(file_path, "r") as yaml_file:
            return yaml.safe_load(yaml_file)

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {file_path}: {e}")

def merge_lists(base_list: List[Any], override_list: List[Any]) -> List[Any]:
    """
    Merge two lists by recursively merging dictionaries found within them.
    """
    merged_list = []

    # Create a set to track sections in the base list for quick lookup
    base_sections = {item.get('section') for item in base_list if isinstance(item, dict)}

    for override_item in override_list:
        if isinstance(override_item, dict):
            # If the override item exists in the base list, merge it
            if override_item.get('section') in base_sections:
                # Find the corresponding base item
                base_item = next(item for item in base_list if item.get('section') == override_item.get('section'))
                merged_list.append(merge_dictionaries(base_item, override_item))
            else:
                # If it doesn't exist in the base, add it directly
                merged_list.append(override_item)
        else:
            # If it's a non-dict, add it directly
            merged_list.append(override_item)

    # Add any remaining items from the base list that were not overridden
    for base_item in base_list:
        if isinstance(base_item, dict) and base_item.get('section') not in {item.get('section') for item in merged_list}:
            merged_list.append(base_item)

    return merged_list


# def merge_lists(base_list: List[Any], override_list: List[Any]) -> List[Any]:
#     """
#     Merge two lists by recursively merging dictionaries found within them.

#     Parameters
#     ----------
#     base_list : list
#         The base list.

#     override_list : list
#         The list with overrides.

#     Returns
#     -------
#     list
#         A new list with merged values.
#     """
#     print(f"[bold][blue][code]Merging lists[/code] >>>[/blue][/bold]")
#     merged_list = []

#     # Create a set to track sections in the base list for quick lookup
#     base_sections = {item.get('section') for item in base_list if isinstance(item, dict)}

#     for override_item in override_list:
#         print(f"{override_item=}")

#         if isinstance(override_item, dict):
#             # If the override item exists in the base list, merge it
#             print(f"- is a [code]dict[code]")
#             print(f"- with {override_item=}")

#             if override_item.get('section') in base_sections:
#                 print(f"- exists in [code]base[/code]")

#                 print(f"Retrieve corresponding {override_item=} from {base_list}")
#                 base_item = next(item for item in base_list if item.get('section') == override_item.get('section'))

#                 print(f"  - [code]Merging dictionaries recursively... [blue]and append to list[/blue][/code] \n")
#                 merged_list.append(merge_dictionaries(base_item, override_item))
#                 print()

#                 print(f"  - [green underline]Updated[/green underline] [code]merged_list[/code] is now {merged_list=}")

#             else:
#                 # If it doesn't exist in the base, add it directly
#                 print(f"- [red]does not exist[/red] in [code]base[/code]")
#                 print(f"  - [code][blue]Append directly to list[/blue][/code] \n")
#                 merged_list.append(override_item)
#                 print(f"  - [green underline]Updated[/green underline] [code]merged_list[/code] is now {merged_list=}")

#         elif isinstance(override_item, list):
#             print(f"- is of type [code]list[code]")
#             print(f"- with {override_item=}")
#             merged_list.append(merge_lists(base_list, override_item))
#             print()
#             print(f"  - [green underline]Updated[/green underline] [code]merged_list[/code] is now {merged_list=}")

#         else:
#             # If it's a non-dict and non-list, add it directly
#             merged_list.append(override_item)

#     # Add any remaining items from the base list that were not overridden
#     for base_item in base_list:
#         if base_item not in merged_list:
#             merged_list.append(base_item)

#     print(f"[bold green]<<< [code]Output[/bold green][/code] is {merged_list=}")
#     return merged_list



def merge_dictionaries(
    base: Dict[str, Any], override: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate a new dictionary by recursively merging the input dictionaries
    'base' and 'override'.

    Parameters
    ----------
    base : dict
        The base dictionary (e.g., a generic template).

    override : dict
        The dictionary with overrides and/or extensions over the base dictionary

    Returns
    -------
    dict
        A new dictionary with `base` updated by `override`.

    Notes
    -----
        The purpose is to support a flexible YAML-based mechanism to generate
        native PVGIS data models in form of Python dictionaries.

    """
    print(f"[bold][magenta][code]Merging dictionaries[/code] >>> >>> >>>[/magenta][/bold]\n")
    print(f"- {base=}\n")
    print(f"- {override=}")
    print()

    import copy
    merged = copy.deepcopy(base)  # Use deep copy to avoid mutability issues
    print(f"[underline]Deep-copying[/underline] the [code]base[/code] to [code]merged[/code]")
    print()

    print(f"Processing keys :\n")

    for key, value in override.items():
        print(f"[underline]{key=} in [code]override[/code][/underline]")# : {value=}")

        if isinstance(value, dict):
            print(f"- is of type [code]dict[code]")# If the key exists in base and is also a dict, merge them
            print(f"- with {value=}")

            if key in merged and isinstance(merged[key], dict):
                print(f"- {key=} exists in [code]merged[/code]")
                print(f"  - is of type [code]dict[/code]")
                print(f"  - with value {merged[key]=}")
                if merged[key] != value:
                    print(f"  - [bold italic orange]hence differs from [/bold italic orange] [code]{key}[/code] in [code]override[/code]")
                    merged[key] = merge_dictionaries(merged[key], value)
                    print(f"  - [green underline]Updated[/green underline] [code]merged[key][/code] is now {merged[key]}")
                else:
                    print(f"  - [bold italic green]is the same as [/bold italic orange] [code]{key}[/code] in [code]override[/code]")

            else:
                print(f"- [red]does not exist in[/red] [code]merged[/code]")
                print(f"  - Adding {key=} to [code]merged[/code]")
                # If the key does not exist in base, just add it
                # merged[key] = copy.deepcopy(value)  # Deep copy to avoid mutability issues
                merged[key] = value
                print(f"  - [green underline]Updated[/green underline] [code]merged[/code] now contains {key=} : {key in merged}")
                print(f"  - See : {merged=}")
                print()

        elif isinstance(value, list):
            print(f"- is of type [code]list[code]")# If the key exists in base and is also a dict, merge them
            print(f"- with {value=}")
            if key in merged and isinstance(merged[key], list):
                print(f"- {key=} exists in [code]merged[/code]")
                print(f"  - with value {merged[key]=}")
                print(f"  - [code]Merging lists recursively[/code] \n")
                # If the key exists in both and is a list, merge the lists
                merged[key] = merge_lists(merged[key], value)
                print()
                print(f" - [dim][underline][green]Updated[/green][/underline] [code][blue]list[/blue][/code] [code]{key}[/code] is now : {merged[key]}[/dim]")
            else:
                # If the key does not exist in merged, just add it
                merged[key] = value
        else:
            print(f"  - [red]is none of types [code]dict, list[code][/red]")# If the key exists in base and is also a dict, merge them
            print(f"  - with value {merged[key]=}")
            if merged[key] != value:
                print(f"  - [bold italic orange]hence differs from [/bold italic orange] [code]{key}[/code] in [code]override[/code]")
            # Override or add new key-value pairs
            print(f"  - [code blue]Overriding or Adding[/code blue] {key=} in [code]merged[/code]")
            merged[key] = value
            print(f"  - [green underline]Updated[/green underline] [code]merged\[{key}][/code] is now {merged[key]}")
            print(f"  - See : {merged=}")
            print()

        print()

    # # Ensure that keys from the base that are not in override are retained
    # for key in base.keys():
    #     if key not in override:
    #         merged.setdefault(key, base[key])  # Retain the base value if not overridden

    print(f"[bold][green]<<< <<< <<< [code]Output[/green][/code][/bold] is {merged=}")
    return merged



def load_data_model(data_model_yaml: Path) -> Dict[str, Any]:
    """
    Load a data model from a YAML file, handling imports recursively.

    Parameters
    ----------
    data_model_yaml : str
        Path to the specific data model YAML file.

    Returns
    -------
    dict
        A merged data model with imports resolved.
    """
    # print(f"{data_model_yaml=}")
    data_model = load_yaml_file(data_model_yaml)

    # Get the name of the data model (the top-level key)
    data_model_name = next(iter(data_model))
    specific_data_model = data_model[data_model_name]

    # Process imports if present
    if "imports" in specific_data_model:
        print(f"Processing [italic]imports[/italic]")
        for import_file in specific_data_model["imports"]:
            print(f'  [dim]Importing base data model [code]{import_file}[/code][/dim] as a dependency for [magenta]{data_model_name}[/magenta].\n')
            base_data_model = load_yaml_file(import_file + ".yaml")

            # Recursively merge imported data with the specific model
            specific_data_model = merge_dictionaries(
                base=base_data_model,
                override=specific_data_model,
            )
            print()

        del specific_data_model["imports"]  # Remove the 'imports' key after processing

    # print(f"- {data_model_name}")
    # print(f"Data model :\n{specific_data_model}")

    # Wrap result back into a dictionary with the data model name as the key
    return {data_model_name: specific_data_model}


def build_python_data_models(
    source_path: Path,
    yaml_files: List[str],
) -> Dict[str, Any]:
    """
    Aggregate multiple data models into a single dictionary.

    Parameters
    ----------
    model_files : list of str
        List of paths to the YAML files defining the models.

    Returns
    -------
    dict
        A dictionary containing all aggregated models.
    """
    data_models = {}

    print(
            f"[bold]PVGIS bases upon a series of native data models. [/bold]"
            f"These are defined in YAML files located in the directory [code]{source_path}[/code]."
            f"\n"
            )
    table = Table(box=None, show_header=False, show_edge=False, pad_edge=False)
    for yaml_file in track(yaml_files, description="Building native data models...\n"):
        data_model = load_data_model(source_path / yaml_file)
        table.add_row(f"- {next(iter(data_model))}")
        data_models.update(data_model)

    Console().print(table)
    print()

    return data_models


def write_to_python_module(models: Dict[str, Any], output_file: Path) -> None:
    """
    Write aggregated models to a Python module as a dictionary.

    Parameters
    ----------
    models : dict
        The aggregated data models.

    output_file : str
        Path to the output Python module file.

    Returns
    -------
        None
    """
    # Build content
    content = (
        f"# Custom data model definitions\n\n"
        f"PVGIS_DATA_MODEL_DEFINITIONS = {models}\n"
    )

    # Write content to Python module file
    try:
        with open(output_file, "w") as python_module:
            python_module.write(content)
        print(f"Python data model definitions written to [code]{output_file}[/code]")

    except IOError as e:
        print(f"Error writing to file \'{output_file}\' : {e}")
