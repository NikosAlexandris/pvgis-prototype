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
    for key, value in override.items():
        if isinstance(value, dict) and key in base and isinstance(base[key], dict):
            # Recursively merge nested dictionaries
            base[key] = merge_dictionaries(base[key], value)
        else:
            # Override or add new key-value pairs
            base[key] = value

    return base


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
        for import_file in specific_data_model["imports"]:
            print(f'[dim]Importing base data model [code]{import_file}[/code][/dim] as a dependency for [magenta]{data_model_name}[/magenta].\n')
            base_data_model = load_yaml_file(import_file + ".yaml")

            # Recursively merge imported data with the specific model
            specific_data_model = merge_dictionaries(
                base=base_data_model,
                override=specific_data_model,
            )

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
