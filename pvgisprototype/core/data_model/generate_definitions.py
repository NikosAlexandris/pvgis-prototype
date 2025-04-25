from typing import Annotated, List
import typer
from pathlib import Path
from pvgisprototype.core.factory.definition.build import build_python_data_models
from pvgisprototype.core.factory.definition.write import write_to_python_module
from yaml_definition_files import PVGIS_DATA_MODEL_YAML_DEFINITION_FILES
import richuru
from richuru import logger, sys


# Configure richuru logger
logger.remove()  # Remove any default handlers
logger.add(sink=sys.stderr, level="DEBUG")  # Add a default sink with INFO level
richuru.install(rich_traceback=True)  # Enable rich traceback for better error visualization

# Typer CLI app setup
app = typer.Typer()
typer_list_of_yaml_files = typer.Option(
    help="List of YAML files with data model definitions",
    rich_help_panel="Input",
    show_default=True,
)


@app.command()
def main(
    source_path: Path = Path("definitions.yaml"),
    definitions: Annotated[List[str], typer_list_of_yaml_files] = PVGIS_DATA_MODEL_YAML_DEFINITION_FILES,
    output_file: Path = Path("definitions.py"),
    verbose: bool = True,
):
    """Build and write Python data models from YAML definitions."""

    # Set logging level based on verbosity
    if verbose:
        logger.level("DEBUG")  # Enable DEBUG-level logging
        logger.debug("Verbose mode enabled.")
    else:
        logger.level("CRITICAL")  # Suppress most logs

    try:
        logger.info(f"Building Python data models from YAML files in {source_path}...")
        pvgis_data_models = build_python_data_models(
            source_path=source_path,
            yaml_files=definitions,
        )

        logger.info(f"Writing data models to {output_file}...")
        write_to_python_module(models=pvgis_data_models, output_file=output_file)
        logger.success("Data models successfully written!")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")


if __name__ == "__main__":
    app()
