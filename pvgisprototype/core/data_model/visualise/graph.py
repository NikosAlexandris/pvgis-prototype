from pathlib import Path
from pvgisprototype.core.data_model.visualise.dependency_graph import build_dependency_graph
from pvgisprototype.core.data_model.visualise.dependency_graph_x import build_dependency_graph_x
from pvgisprototype.core.data_model.visualise.dependency_graph_xx import build_dependency_graph_xx
from pvgisprototype.core.data_model.visualise.sort import topological_sort
from pvgisprototype.core.data_model.visualise.visualise import (
    visualize_graph,
    visualize_hierarchical_graph,
)
from pvgisprototype.core.data_model.visualise.visualise_x import visualize_graph_x
from pvgisprototype.core.data_model.visualise.visualise_xx import visualize_graph_xx


def generate_graph(
    source_path: Path,
) -> None:
    """
    """
    # Build graph
    graph = build_dependency_graph(source_path=source_path)
    
    # Topological sort
    order = topological_sort(graph)
    print("Topological Order:", order)
    
    # Visualize
    visualize_graph(graph)


def generate_graph_x(
    source_path: Path,
    yaml_file: Path,
) -> None:
    """
    """
    # Build graph
    graph = build_dependency_graph_x(source_path=source_path, yaml_file=yaml_file)
    
    # Topological sort
    order = topological_sort(graph)
    print("Topological Order:", order)
    
    # Visualize
    visualize_graph_x(graph)


def generate_graph_xx(
    source_path: Path,
    yaml_file: Path,
) -> None:
    """
    """
    # Build graph
    graph = build_dependency_graph_xx(
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
    # print("Topological Order:", order)
    
    # Visualize
    visualize_graph_xx(graph)


def generate_hierarchical_graph(
    source_path: Path,
) -> None:
    """
    """
    # Build graph
    graph = build_dependency_graph(source_path=source_path)
    
    # Topological sort
    order = topological_sort(graph)
    print("Topological Order:", order)
    
    # Visualize
    visualize_hierarchical_graph(graph)


if __name__ == "__main__":
    data_models_dir = Path("")
    generate_graph(data_models_dir)
