from typing import Annotated
import typer
from pathlib import Path

from pvgisprototype.core.data_model.graph.generate import (
    generate_circular_tree,
    generate_gravis_d3,
    generate_graph,
    generate_hierarchical_graph,
)

def visualise_gravis_d3(
    ctx: typer.Context,  # Access parent context
    source_path: Annotated[
        Path, typer.Option(help="Source directory with YAML data model descriptions")
    ] = Path(
        "definitions.yaml"
    ),  # definitions.yaml"),
    # yaml_file: Path = Path("definitions.yaml/data_model_template.yaml"),
    output_file: Path = Path("data_model_graph.html"),
    # node_size: Annotated[int, typer.Option(help="Node size")] = 2400,
    # parent_node_size: Annotated[int, typer.Option(help="Parent node size")] = 800,
) -> None:
    """
    Prototype for the command line
    """
    # Get logging config from parent context if available
    log_config = getattr(ctx.obj, 'log_config', {}) if ctx and ctx.obj else {}
    generate_gravis_d3(
        source_path=source_path,
        # yaml_file=yaml_file,
        output_file=output_file,
        # node_size=node_size,
        # parent_node_size=parent_node_size,
        **log_config
    )

    
def visualise_graph(
    source_path: Annotated[
        Path, typer.Option(help="Source directory with YAML data model descriptions")
    ] = Path(
        "output/complex_example"
    ),  # definitions.yaml"),
    # yaml_file: Path = Path("output/complex_example/complex.yaml"),
    node_size: Annotated[int, typer.Option(help="Node size")] = 2400,
    parent_node_size: Annotated[int, typer.Option(help="Parent node size")] = 800,
) -> None:
    """
    Prototype for the command line
    """
    generate_graph(
        source_path=source_path,
        # yaml_file=yaml_file,
        node_size=node_size,
        parent_node_size=parent_node_size,
    )


def visualise_circular_tree(
    source_path: Annotated[
        Path, typer.Option(help="Source directory with YAML data model descriptions")
    ] = Path(
        "output/complex_example"
    ),  # definitions.yaml"),
    node_size: Annotated[int, typer.Option(help="Node size")] = 20,
) -> None:
    """
    Prototype for the command line
    """
    generate_circular_tree(
        source_path=source_path,
        node_size=node_size,
    )


def visualise_hierarchical_graph(
    source_path: Annotated[
        Path, typer.Option(help="Source directory with YAML data model descriptions")
    ] = Path(
        "output/complex_example"
    ),  # definitions.yaml"),
) -> None:
    """
    Prototype for the command line
    """
    generate_hierarchical_graph(source_path)
