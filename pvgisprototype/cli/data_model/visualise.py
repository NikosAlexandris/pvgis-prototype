from typing import Annotated
import typer
from pathlib import Path

from pvgisprototype.core.data_model.visualise.graph import (
    generate_graph,
    generate_graph_x,
    generate_graph_xx,
    generate_hierarchical_graph,
)


def visualise_graph(
    source_path: Annotated[
        Path, typer.Option(help="Source directory with YAML data model descriptions")
    ] = Path(
        "output/complex_example"
    ),  # definitions.yaml"),
) -> None:
    """
    Prototype for the command line
    """
    generate_graph(source_path)


def visualise_graph_x(
    source_path: Annotated[
        Path, typer.Option(help="Source directory with YAML data model descriptions")
    ] = Path(
        "output/complex_example"
    ),  # definitions.yaml"),
    yaml_file: Path = Path("output/complex_example/complex.yaml"),
) -> None:
    """
    Prototype for the command line
    """
    generate_graph_x(source_path, yaml_file)


def visualise_graph_xx(
    source_path: Annotated[
        Path, typer.Option(help="Source directory with YAML data model descriptions")
    ] = Path(
        "output/complex_example"
    ),  # definitions.yaml"),
    yaml_file: Path = Path("output/complex_example/complex.yaml"),
) -> None:
    """
    Prototype for the command line
    """
    generate_graph_xx(source_path, yaml_file)


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
