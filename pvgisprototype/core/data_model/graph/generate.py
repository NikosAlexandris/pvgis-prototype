from pvgisprototype.core.factory.log import logger
from pathlib import Path
from pvgisprototype.core.data_model.graph.circular_tree import visualise_circular_tree
from pvgisprototype.core.data_model.graph.build import build_dependency_graph
from pvgisprototype.core.data_model.graph.sort import topological_sort
from pvgisprototype.core.data_model.graph.gravis_ import visualise_gravis_d3
from pvgisprototype.core.data_model.graph.graphviz_ import (
    visualise_graph,
    visualise_hierarchical_graph,
)


def generate_gravis_d3(
    source_path: Path,
    yaml_file: Path,
    output_file: Path,
    # node_size: int = 2400,
    # parent_node_size: int = 1200,
    verbose: bool = False,
    log_level: str = "WARNING",
    log_file: Path | None = None,
    rich_handler: bool = False,
) -> None:
    """
    """
    graph = build_dependency_graph(
        source_path=source_path,
        verbose=verbose,
        log_level=log_level,
        log_file=log_file,
        rich_handler=rich_handler,
    )
    logger.debug(f"{graph.nodes()=}\n{graph.edges()=}")
    output_file = Path(yaml_file.name).with_suffix('.html')
    visualise_gravis_d3(
        graph=graph,
        output_file=output_file,
        # node_size=node_size,
        # parent_node_size=parent_node_size,
        # log_level=log_level,
        # log_file=log_file,
        # rich_handler=rich_handler,
    )


def generate_graph(
    source_path: Path,
    yaml_file: Path,
    node_size: int = 2400,
    parent_node_size: int = 1200,
) -> None:
    """
    """
    # Build graph
    graph = build_dependency_graph(
        source_path=source_path,
    )
    
    # # Topological sort
    # import networkx as nx
    # def topological_sort(G: nx.DiGraph) -> list:
    #     try:
    #         return list(nx.topological_sort(G))
    #     except nx.NetworkXUnfeasible:
    #         raise ValueError("Graph contains a cycle")

    # order = topological_sort(graph)
    # logger.debug("Topological Order:", order)
    
    # Visualize
    visualise_graph(
        graph=graph,
        node_size=node_size,
        parent_node_size=parent_node_size,
    )


def generate_circular_tree(
    source_path: Path,
    # yaml_file: Path,
    node_size: int = 20,
) -> None:
    """
    """
    # Build graph
    graph = build_dependency_graph(
        source_path=source_path,
    )
    
    # # Topological sort
    # import networkx as nx
    # def topological_sort(G: nx.DiGraph) -> list:
    #     try:
    #         return list(nx.topological_sort(G))
    #     except nx.NetworkXUnfeasible:
    #         raise ValueError("Graph contains a cycle")

    # order = topological_sort(graph)
    # logger.debug("Topological Order:", order)
    
    # Visualize
    visualise_circular_tree(
        graph=graph,
        node_size=node_size,
    )


def generate_hierarchical_graph(
    source_path: Path,
) -> None:
    """
    """
    # Build graph
    graph = build_dependency_graph(source_path=source_path)
    
    # Topological sort
    order = topological_sort(graph)
    logger.debug("Topological Order:", order)
    
    visualise_hierarchical_graph(graph)


if __name__ == "__main__":
    data_models_dir = Path("")
    generate_graph(data_models_dir)
