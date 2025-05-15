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
from pvgisprototype.cli.data_model.analyse import (
    analyse_graph,
    detect_cycles_and_strongly_connected_components,
    analyse_dependency_structure,
    analyse_centrality,
    detect_densely_connected_components,
    analyse_path_length,
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

analyse_data_model_dependency_graph_help = (
    "Summary of Key Metrics  "
    + "Metric 	PVGIS Implication 	Example Tool\n"
    + "Cycles 	Circular dependencies → code smell 	nx.simple_cycles\n"
    + "SCCs 	Tightly interdependent modules nx.strongly_connected_components\n"
    + "Betweenness 	Critical models acting as bridges nx.betweenness_centrality\n"
    + "Communities 	Modular structure (e.g., solar vs. PV models) nx_comm.greedy_modularity_communities\n"
    + "Topological Order 	Processing order for dependencies nx.topological_sort"
)
analyse_app = typer.Typer(
    # cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    # help="! Analyse the graph of data model definition (YAML file)",
    help=analyse_data_model_dependency_graph_help,
)
visualise_app = typer.Typer(
    # cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help="* Visualise data model definitions",
)
app.add_typer(
    typer_instance=inspect_app,
    name="inspect",
    no_args_is_help=True,
    # rich_help_panel='',
)
app.add_typer(
    typer_instance=analyse_app,
    name="analyse",
    no_args_is_help=True,
    # rich_help_panel='',
)
app.add_typer(
    typer_instance=visualise_app,
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
analyse_app.command(
    name='graph',
    help="Analyse graph metrics of a data model",
    no_args_is_help=True,
    rich_help_panel='Analyse',
)(analyse_graph)
analyse_app.command(
    name='cycles',
    help="Analyse graph metrics of a data model",
    no_args_is_help=True,
    rich_help_panel='Analyse',
)(detect_cycles_and_strongly_connected_components)
analyse_app.command(
    name='structure',
    help="Analyse the dependency structure of a data model",
    no_args_is_help=True,
    rich_help_panel='Analyse',
)(analyse_dependency_structure)
analyse_app.command(
    name='centrality',
    help="Identify critical data models (nodes)",
    no_args_is_help=True,
    rich_help_panel='Analyse',
)(analyse_centrality)
analyse_app.command(
    name='density',
    help="Detect densely connected data models (nodes)",
    no_args_is_help=True,
    rich_help_panel='Analyse',
)(detect_densely_connected_components)
analyse_app.command(
    name='path',
    help="Analyse path length and reachability",
    no_args_is_help=True,
    rich_help_panel='Analyse',
)(analyse_path_length)
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
