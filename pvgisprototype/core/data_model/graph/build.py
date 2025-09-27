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
from rich.progress import track
from collections import deque
import yaml
from pathlib import Path
import networkx as nx
from pvgisprototype.core.factory.log import logger
from pvgisprototype.core.factory.definition.merge import deep_merge


def resolve_require_path(base_dir: Path, require_path: str) -> Path:
    """
    Resolve require path (e.g., 'sun/position') to a YAML file (e.g., 'sun/position.yaml').
    """
    path = (base_dir / require_path).with_suffix('.yaml')
    # logger.debug(f"[blue]Resolved path to parent node[/blue] {path=}")
    return path


def process_model(
    graph: nx.DiGraph,
    base_dir: Path,
    require_path: str,
    yaml_path: Path,
    queue: deque,
    visited: dict,
):
    """
    Process a YAML file and its dependencies
    """
    logger.debug(f"Input graph\n   {graph.nodes=}\n   {graph.edges=}\n")
    # logger.debug(
    #     f"Processing\n\n   {graph.nodes()=}\n\n   YAML file {yaml_path=}",
    # )
    logger.debug(
        "Processing YAML file {yaml_path}",
        yaml_path=yaml_path,
        alt=f"Processing YAML file {yaml_path=}"
    )
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        logger.debug(f"Loaded data\n   {data=}")

    model_name = data.get('name')  # required
    visited[require_path] = model_name
    
    # Merge parent attributes if inheriting
    if 'require' in data:
        for parent_require in track(data['require'], description="Resolving requirements"):
            logger.debug(f"Processing require directive {base_dir=} / {require_path=} = {parent_require=}")
            parent_path = resolve_require_path(base_dir=base_dir, require_path=parent_require)
            logger.debug(f"Path to parent node {parent_path=}")
            if parent_path.exists():
                logger.debug(f"Loading {parent_path=}")
                with open(parent_path, 'r') as pf:
                    parent_data = yaml.safe_load(pf)
                    # Recursive attribute merging
                logger.debug(f"Merging\n\n   {parent_data}\n\nand\n\n   {data=}\n")
                data = deep_merge(
                    base=parent_data,
                    override=data,
                )
                logger.debug(f"Merged\n\n   {data=}\n")

    # Get meaninfgul attributes
    model_symbol = data.get('symbol', '')
    model_label = data.get('label', '')
    model_label += f" {model_symbol}"
    model_description = data.get('description')  # required
    model_attributes = data.get('sections', '')
    model_color = data.get('color', 'white')

    # Add node with merged attributes
    logger.debug(
            f"Adding {model_name=} to graph"
            )
    
    # ---------------------------------------------------------------------
    # graph.add_node(
    #     node_for_adding=model_name,
    #     **{key: value for key, value in data.items() if key != "require"},
    #     _source_path=str(yaml_path),
    # )
    # ---------------------------------------------------------------------
    graph.add_node(
        node_for_adding=model_name,
        label=model_label,
        description=model_description,
        symbol=model_symbol,
        attributes=model_attributes,
        color=model_color,
        border_color='lightgray',
        border_size=1,
        hover=model_description,
        click=yaml.dump(data=model_attributes, allow_unicode=True),#, encoding='utf-8'),
    )

    logger.debug(
        f"   [bold dim]Updated graph nodes\n      {graph.nodes[model_name]=}\n"
    )

    # Process dependencies
    requires = data.get('require', [])
    logger.debug(f"[bold blue]Require directives to process[/bold blue]\n\n   {requires=}\n")

    for parent_node in requires:

        logger.debug(f"[bold blue]Processing parent node[/bold blue] {parent_node=}")
        parent_node_path = resolve_require_path(base_dir, parent_node)
        parent_node_label = parent_node_path.parts[-2]

        # logger.debug(f"{parent_node_path.exists()=}")
        if not parent_node_path.exists():
            logger.debug(f"Continue ?")
            continue
            
        if parent_node not in visited:
            logger.debug(f"[blue dim]Appending to processing queue[/blue dim] {parent_node=}")
            queue.append((parent_node, parent_node_path))
            with open(parent_node_path, 'r', encoding='utf-8') as parent_node_file:
                parent_node = yaml.safe_load(parent_node_file)
            parent_node_name = parent_node.get('name', '<Unnamed node>')
        
        else:
            logger.debug(f"[blue]Already visited[/blue] {parent_node=}, see\n\n   {visited=}")
            parent_node_name = visited[parent_node]

        
        # Add edge even if parent not processed yet
        graph.add_edge(
            u_of_edge=model_name,
            v_of_edge=parent_node_name or parent_node,
            label=parent_node_label,
            color='lightgray',
        )
        # logger.debug(f"Updated edges\n      {graph.edges=}\n")
        # logger.debug(f"Nodes after new edge addition\n      {graph.nodes=}\n")

    logger.debug(f"Updated graph\n   {graph.nodes=}\n   {graph.edges=}\n")


def build_dependency_graph(
    source_path: Path,
    verbose: bool = False,
    log_level: str = "WARNING",
    log_file: Path | None = None,
    rich_handler: bool = False,
) -> nx.DiGraph:
    """
    Build a recursive dependency graph from YAML files.
    """
    # # Only set up logging if not already configured
    # if not any(
    #     handler.levelno <= getattr(logger, log_level.upper())
    #     for handler in logger._core.handlers.values()
    # ):
    #  Initialize logging
    # setup_factory_logger(
    #     verbose=verbose,
    #     level=log_level,
    #     file=log_file,
    #     rich_handler=rich_handler,
    # )

    base_dir = Path(source_path.parts[0])
    logger.debug(f"Base directory : {base_dir=}")
    # base_dir = Path(source_path.parts[0]) if source_path.is_dir() else source_path.parents[1]

    graph = nx.DiGraph()
    visited = {}  # Maps require path -> model name
    queue = deque()

    if source_path.is_file() and source_path.suffix == '.yaml':
        queue.append((source_path.name, source_path))
        logger.debug(f"Data appended to queue which now is {queue=}")

    elif source_path.is_dir():
        yaml_files = source_path.rglob("*.yaml")
        for yaml_file in track(yaml_files, description="Queueing data models for processing\n" ):
            queue.append((yaml_file.name, yaml_file))

    while queue:
        # logger.debug(f"[underline]The queue is now[/underline]\n\n   {queue=}\n")
        req_name, yaml_path = queue.popleft()
        # logger.debug(f"[dim]After poping\n\n  {queue=}[/dim]\n")
        logger.debug(f"In the queue : {req_name=} {yaml_path=}")
        if req_name in visited:
            logger.debug(f"[red dim]{req_name=} already processed ![/red dim]")
            continue  # Already processed

        process_model(
            graph=graph,
            base_dir=base_dir,
            require_path=req_name,
            yaml_path=yaml_path,
            queue=queue,
            visited=visited,
        )

    # logger.debug("Return dependency graph G\n\n{graph}", G=graph)
    # logger.debug(f"Return {graph.nodes()=}")
    return graph
