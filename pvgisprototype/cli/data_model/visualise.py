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
    yaml_file: Annotated[
        Path, typer.Option(help="A YAML PVGIS data model description")
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
        yaml_file=yaml_file,
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
