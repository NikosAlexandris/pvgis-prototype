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

# from rich.panel import Panel
from typing import Annotated
import typer
# from pvgisprototype.core.data_model.visualise.graph import generate_graph, generate_hierarchical_graph
from pvgisprototype.cli.data_model.inspect import inspect_pvgis_data_model, inspect_python_definition, inspect_yaml_definition
from pvgisprototype.cli.data_model.visualise import (
    visualise_circular_tree,
    visualise_gravis_d3,
    visualise_graph,
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
from pvgisprototype.constants import SYMBOL_DATA_MODEL
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
    help=f"{SYMBOL_DATA_MODEL} Tooling for PVGIS' Data Model",
)
inspect_app = typer.Typer(
    # cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help="! Inspect data model definitions including YAML files, Python dictionaries and native PVGIS data models",
)

analyse_data_model_dependency_graph_help = (
    # "Summary of Key Metrics  "
    "[Metric, Implication → Example Tool]\n"
    + "Cycles, Circular dependencies (code smell?) → nx.simple_cycles\n"
    + "SCCs, Tightly interdependent modules → nx.strongly_connected_components\n"
    + "Betweenness,	Critical models acting as bridges → nx.betweenness_centrality\n"
    + "Communities,	Modular structure → nx_comm.greedy_modularity_communities\n"
    + "Topological Order, Processing order for dependencies → nx.topological_sort"
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
    ctx: typer.Context,
    verbose: Annotated[bool, typer.Option(help="Verbose")] = False,
    log_file: Annotated[
        str | None, typer.Option("--log-file", "-l", help="Log file")
    ] = LOG_FILE,
    log_level: str = LOG_LEVEL,
    rich_handler: Annotated[
        bool, typer.Option("--rich", "--no-rich", help="Rich handler")
    ] = RICH_HANDLER,
):
    """
    Inspect data model definitions including YAML files, Python dictionaries
    and native PVGIS data models.
    """
    if verbose:
        log_level = "DEBUG"
    setup_factory_logger(level=log_level, file=log_file, rich_handler=rich_handler)

    # Store logging config in context for child commands
    if not ctx.obj:
        ctx.obj = {}
    ctx.obj["logger_configuration"] = {
        "log_level": log_level,
        "log_file": log_file,
        "rich_handler": rich_handler,
    }


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
    name='gravis-d3',
    help="Visualise a nested data model as a graph using gravis-d3",
    no_args_is_help=True,
    rich_help_panel='Visualise',
)(visualise_gravis_d3)
visualise_app.command(
    name='graph',
    help="Visualise a nested data model as a graph",
    no_args_is_help=True,
    rich_help_panel='Visualise',
)(visualise_graph)
visualise_app.command(
    name='circular-tree',
    help="Visualise a nested data model as a circular tree",
    no_args_is_help=True,
    rich_help_panel='Visualise',
)(visualise_circular_tree)
visualise_app.command(
    name='hierarchical-graph',
    help="Visualise a data model as a graph",
    no_args_is_help=True,
    rich_help_panel='Visualise',
)(visualise_hierarchical_graph)
