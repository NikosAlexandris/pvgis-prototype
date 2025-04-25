from pathlib import Path
from pvgisprototype.log import logger
from typing import Dict, Any


def write_to_python_module(models: Dict[str, Any], output_file: Path) -> None:
    """Write aggregated models to a Python module as a dictionary."""
    content = (
        f"# Custom data model definitions\n\n"
        f"PVGIS_DATA_MODEL_DEFINITIONS = {models}\n"
    )

    try:
        with open(output_file, "w") as python_module:
            python_module.write(content)
        logger.debug(
            "",
            alt=f"Python data model definitions written to [code]{output_file}[/code]"
        )
    except IOError as e:
        print(f"Error writing to file '{output_file}' : {e}")
