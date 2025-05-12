# from rich.panel import Panel
from typing import Annotated
import typer
# from pvgisprototype.core.data_model.visualise.graph import generate_graph, generate_hierarchical_graph
from pvgisprototype.cli.data_model.inspect import inspect_pvgis_data_model, inspect_python_definition, inspect_yaml_definition
from pvgisprototype.cli.data_model.visualise import (
    visualise_graph,
    visualise_graph_x,
    visualise_graph_xx,
    visualise_hierarchical_graph,
)
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
inspect_app = typer.Typer(
    # cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help="! Inspect data model definitions including YAML files, Python dictionaries and native PVGIS data models",
)
visualise_app = typer.Typer(
    # cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help="* Visualise data model definitions",
)
app.add_typer(
    inspect_app,
    name="inspect",
    no_args_is_help=True,
    # rich_help_panel='',
)
app.add_typer(
    visualise_app,
    name="visualise",
    no_args_is_help=True,
    # rich_help_panel='',
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


inspect_app.command(
    name="yaml-file",
    help=f"YAML",
    no_args_is_help=True,
    rich_help_panel='Inspect',
)(inspect_yaml_definition)
inspect_app.command(
    name="python-dictionary",
    help=f"Python",
    no_args_is_help=True,
    rich_help_panel='Inspect',
)(inspect_python_definition)
inspect_app.command(
    name="pvgis-data-model",
    help=f"Python",
    no_args_is_help=True,
    rich_help_panel='Inspect',
)(inspect_pvgis_data_model)
visualise_app.command(
    name='graph',
    help="Visualise a data model as a graph",
    no_args_is_help=True,
    rich_help_panel='Visualise',
)(visualise_graph)
visualise_app.command(
    name='graph-x',
    help="Visualise a nested data model as a graph",
    no_args_is_help=True,
    rich_help_panel='Visualise',
)(visualise_graph_x)
visualise_app.command(
    name='graph-xx',
    help="Visualise a nested data model as a graph",
    no_args_is_help=True,
    rich_help_panel='Visualise',
)(visualise_graph_xx)
visualise_app.command(
    name='hierarchical-graph',
    help="Visualise a data model as a graph",
    no_args_is_help=True,
    rich_help_panel='Visualise',
)(visualise_hierarchical_graph)
