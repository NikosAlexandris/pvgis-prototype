from pathlib import Path
from typing import Dict, Any
import yaml
from pathlib import Path
from typing import Any, Dict
from pvgisprototype.core.factory.log import logger


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """
    Load a data model definition from a properly structured YAML file into a
    Python dictionary.
    """
    try:
        logger.debug(
            "Loading {file_path}...",
            file_path=file_path,
            alt=f"Loading [bold]{file_path.as_posix()}[/bold]...",
        )
        with open(file_path, "r") as yaml_file:
            return yaml.safe_load(yaml_file)
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")

    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {file_path}: {e}")
