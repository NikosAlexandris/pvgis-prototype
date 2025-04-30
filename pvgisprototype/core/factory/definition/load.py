from richuru import logger
from pathlib import Path
import yaml
from typing import Dict, Any
from pvgisprototype.core.factory.definition.merge import merge_dictionaries


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Load a YAML file and return its contents as a dictionary."""
    try:
        logger.debug(
            f"   Reading file {file_path}...",
            alt=f"   [bold]Reading[/bold] {file_path}..."
            )
        with open(file_path, "r") as yaml_file:
            return yaml.safe_load(yaml_file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {file_path}: {e}")


def load_data_model(source_path: Path, data_model_yaml: Path) -> Dict[str, Any]:
    data_model = load_yaml_file(data_model_yaml)
    data_model_name = data_model["name"]
    # logger.info("", alt=f"Processing data model [bold]{data_model_name=}[/bold]")
    data_model_fields = data_model["fields"]

    if "imports" in data_model:
        for import_file in data_model["imports"]:
            imported_path = (source_path / import_file).with_suffix(".yaml")
            imported_data = load_data_model(source_path, imported_path)
            imported_data_name = next(iter(imported_data))
            data_model_fields = merge_dictionaries(
                base=imported_data[imported_data_name],
                override=data_model_fields,
            )

    return {data_model_name: data_model_fields}
