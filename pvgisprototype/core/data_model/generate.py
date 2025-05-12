from typing import Annotated, List
import typer
from pathlib import Path
from pvgisprototype.core.factory.definition.build import build_python_data_models
from pvgisprototype.core.factory.definition.write import reset_python_data_model_definitions, write_to_python_module
from yaml_definition_files import PVGIS_DATA_MODEL_YAML_DEFINITION_FILES

from pvgisprototype.core.factory.log import logger
from pvgisprototype.core.factory.log import setup_factory_logger
from typer import Context
import os


LOG_LEVEL = os.getenv("FACTORY_LOG_LEVEL", "WARNING").upper()
LOG_FILE = os.getenv("FACTORY_LOG_FILE")
RICH_HANDLER = os.getenv("FACTORY_RICH", "true").lower() == "false"


def callback_reset_python_data_model_definitions(
    ctx: Context,
    reset_definitions: bool,
):
    """
    """
    # print(ctx.params)
    if not reset_definitions:
        return
    else:
        output_file = ctx.params.get('output_file')
        verbose = ctx.params.get('verbose')
        print(f"Reset the Python definition dictionary in {output_file} an empty one !")
        reset_python_data_model_definitions(
            output_file=output_file,
            verbose=verbose,
        )
        raise typer.Exit()


# Typer CLI app setup
app = typer.Typer()
typer_list_of_yaml_files = typer.Option(
    help="List of YAML files with data model definitions",
    rich_help_panel="Input",
    show_default=True,
)
typer_option_reset_definitions = typer.Option(
    help="Reset the Python definitions dictionary to an empty one! ",
    # is_eager=True,
    is_flag=True,
    show_choices=True,
    callback=callback_reset_python_data_model_definitions,
)

@app.command()
def main(
    source_path: Annotated[Path, typer.Option(help="Source directory with YAML data model descriptions")] = Path("definitions.yaml"),
    definitions: Annotated[List[str], typer_list_of_yaml_files] = PVGIS_DATA_MODEL_YAML_DEFINITION_FILES,
    output_file: Annotated[Path, typer.Option(help='Output file', is_eager=True)] = Path("definitions.py"),
    verbose: Annotated[bool, typer.Option(help="Verbose")] = False,
    log_file: Annotated[str | None, typer.Option("--log-file", "-l",help="Log file")] = LOG_FILE,
    log_level: str = LOG_LEVEL,
    rich_handler: Annotated[bool, typer.Option("--rich", "--no-rich", help="Rich handler")] = RICH_HANDLER,
    reset_definitions: Annotated[bool, typer_option_reset_definitions] = False, # I am a callback  function !
):
    """
    Build and write Python data models from YAML definitions.
    """
    #  Initialize logging
    setup_factory_logger(
            verbose=verbose,
            level=log_level,
            file=log_file,
            rich_handler=rich_handler,
    )

    try:
        reset_python_data_model_definitions(output_file=output_file, verbose=verbose)
        pvgis_data_models = build_python_data_models(
            source_path=source_path,
            yaml_files=definitions,
            verbose=verbose,
        )
        write_to_python_module(models=pvgis_data_models, output_file=output_file, verbose=verbose)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
    else:
        if verbose:
            logger.success("Data models successfully generated !")


if __name__ == "__main__":
    app()
