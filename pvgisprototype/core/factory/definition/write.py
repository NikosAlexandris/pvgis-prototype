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
from pvgisprototype.core.factory.log import logger
from typing import Dict, Any


def write_to_python_module(
    models: Dict[str, Any],
    output_file: Path,
    verbose: bool = False,
) -> None:
    """Write aggregated models to a Python module as a dictionary."""
    try:
        content = (
            f"# Custom data model definitions\n\n"
            f"PVGIS_DATA_MODEL_DEFINITIONS = {models}\n"
        )
        if verbose and models:
            logger.info("", alt=f"[bold]Writing[/bold] to [code]{output_file}[/code]")

        with open(output_file, "w") as python_module:
            python_module.write(content)

    except IOError as e:
        print(f"Error writing to file '{output_file}' : {e}")
    
    logger.debug("", alt=f"Python data model definitions written to [code]{output_file}[/code]")


def reset_python_data_model_definitions(
    output_file: Path,
    verbose: bool = False,
) -> None:
    """Reset to empty dictionary !"""
    if verbose:
        logger.info("", alt=f"[bold]Reseting[/bold] [code]{output_file}[/code] to an empty dictionary")
    write_to_python_module(models={}, output_file=output_file)
