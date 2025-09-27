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
