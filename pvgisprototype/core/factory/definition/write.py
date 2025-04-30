from pathlib import Path
from pvgisprototype.log import logger
from typing import Dict, Any


def write_to_python_module(models: Dict[str, Any], output_file: Path, verbose: bool = False) -> None:
    """Write aggregated models to a Python module as a dictionary."""
    content = (
        f"# Custom data model definitions\n\n"
        f"PVGIS_DATA_MODEL_DEFINITIONS = {models}\n"
    )

    try:
        if verbose and models:
            logger.info("", alt=f"[bold]Writing[/bold] to [code]{output_file}[/code]")
        with open(output_file, "w") as python_module:
            python_module.write(content)
    except IOError as e:
        print(f"Error writing to file '{output_file}' : {e}")
    except:
        logger.debug("", alt=f"Python data model definitions written to [code]{output_file}[/code]")


def reset_python_data_model_definitions(output_file: Path, verbose: bool = False) -> None:
    """Reset to empty dictionary !"""
    if verbose:
        logger.info("", alt=f"[bold]Reseting[/bold] [code]{output_file}[/code] to an empty dictionary")
    write_to_python_module(models={}, output_file=output_file)
