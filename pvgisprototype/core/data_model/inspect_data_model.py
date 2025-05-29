# from rich.panel import Panel
from typing import Annotated
import typer
# from pvgisprototype.core.data_model.visualise.graph import generate_graph, generate_hierarchical_graph
from yaml_definition_files import PVGIS_DATA_MODEL_YAML_DEFINITION_FILES
from pvgisprototype.core.factory.log import setup_factory_logger


import os
LOG_LEVEL = os.getenv("FACTORY_LOG_LEVEL", "WARNING").upper()
LOG_FILE = os.getenv("FACTORY_LOG_FILE")
RICH_HANDLER = os.getenv("FACTORY_RICH", "true").lower() == "true"


# typer.rich_utils.Panel = Panel.fit

app = typer.Typer(
    # cls=OrderCommands,
    no_args_is_help=True,
    add_completion=False,
    add_help_option=True,
    rich_markup_mode="rich",
    # pretty_exceptions_enable=False,
    help="PVGIS Command Line Interface [bold][magenta]prototype[/magenta][/bold]",
)


@app.callback()
def main(
    verbose: Annotated[bool, typer.Option(help="Verbose")] = False,
    log_file: Annotated[str | None, typer.Option("--log-file", "-l",help="Log file")] = LOG_FILE,
    log_level: str = LOG_LEVEL,
    rich_handler: Annotated[bool, typer.Option("--rich", "--no-rich", help="Rich handler")] = RICH_HANDLER,
):
    """
    Inspect data model definitions including YAML files, Python dictionaries
    and native PVGIS data models.
    """
    if verbose:
        log_level = "DEBUG"
    setup_factory_logger(level=log_level, file=log_file, rich_handler=rich_handler)


if __name__ == "__main__":
    app()
