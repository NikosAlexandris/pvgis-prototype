from pathlib import Path
from pvgisprototype.core.data_model.graph.build import build_dependency_graph
from pvgisprototype.core.factory.definition.load import load_yaml_file
import networkx as nx
from rich import print
import networkx.algorithms.community as nx_comm


def analyse_graph(
    source_path: Path,
) -> None:
    """
    Calculate fundamental metrics to understand the scale and density of
    dependencies.
    - High node/edge counts suggest complexity.
    - High density (many edges relative to nodes) indicates tightly
      interconnected models, which may complicate maintenance.

    """
    graph = build_dependency_graph(source_path=source_path)
    print(f"Number of nodes (models): {graph.number_of_nodes()}")
    print(f"Number of edges (dependencies): {graph.number_of_edges()}")
    print(f"Graph density: {nx.density(G=graph):.4f}")
    print(
        f"Is the graph a DAG (Directed Acyclic Graph)? {nx.is_directed_acyclic_graph(G=graph)}"
    )


def detect_cycles_and_strongly_connected_components(
    source_path: Path,
) -> None:
    """
    - Cycles (e.g., A → B → A) indicate potential design flaws.
    - Large Strongly Connected Components suggest tightly interdependent
      modules needing refactoring.

    """
    graph = build_dependency_graph(source_path=source_path)
    try:
        cycles = list(nx.simple_cycles(G=graph))
        print(f"Found {len(cycles)} cycles. Examples:")
        for cycle in cycles[:3]:  # Show first 3
            print(" → ".join(cycle))

    except nx.NetworkXNoCycle:
        print("No cycles detected.")

    strongly_connected_components = list(nx.strongly_connected_components(G=graph))

    print("Strongly Connected Components")
    print(f"Number of components : {len(strongly_connected_components)}")
    print(
        "Largest component :",
        (
            max(strongly_connected_components, key=len)
            if strongly_connected_components
            else "N/A"
        ),
    )


def analyse_dependency_structure(
    source_path: Path,
) -> None:
    """
    A long critical path suggests a deep dependency chain, which may impact
    performance or testing complexity.

    """
    graph = build_dependency_graph(source_path=source_path)
    if nx.is_directed_acyclic_graph(G=graph):
        topological_order = list(nx.topological_sort(G=graph))
        print("Topological order (first 5):", topological_order[:5])

        # Longest path (critical path)
        longest_path = nx.dag_longest_path(G=graph)
        print(f"Critical path length: {len(longest_path)}")
        print(f"Critical path: {longest_path}")

    else:
        print("Graph is not a DAG. Skipping topological analysis.")


def analyse_centrality(
    source_path: Path,
) -> None:
    """
    Identify critical nodes (models) that act as hubs or bridges
    - High in-degree nodes are critical for many models.
    - High betweenness nodes act as bridges between modules.

    """
    graph = build_dependency_graph(source_path=source_path)
    in_degrees = dict(graph.in_degree())
    out_degrees = dict(graph.out_degree())
    betweenness = nx.betweenness_centrality(graph)
    pagerank = nx.pagerank(graph)

    print("Top 5 nodes by in-degree (most dependencies) :")
    for node in sorted(in_degrees, key=in_degrees.get, reverse=True)[:5]:
        print(f"{node}: {in_degrees[node]}")

    print("\nTop 5 nodes by out-degree (most ) :")
    for node in sorted(out_degrees, key=out_degrees.get, reverse=True)[:5]:
        print(f"{node}: {out_degrees[node]}")

    print("\nTop 5 nodes by betweenness centrality (bridges) :")
    for node in sorted(betweenness, key=betweenness.get, reverse=True)[:5]:
        print(f"{node}: {betweenness[node]:.4f}")

    print("\nTop 5 nodes by PageRank (influence) :")
    for node in sorted(pagerank, key=pagerank.get, reverse=True)[:5]:
        print(f"{node}: {pagerank[node]:.4f}")


def detect_densely_connected_components(
    source_path: Path,
) -> None:
    """
    Detect clusters of densely connected models to assess modularity


    Interpretation:
    - Communities may align with functional domains (e.g., solar position,
      energy yield, temperature).
    - High modularity suggests well-organized, maintainable code.

    """
    graph = build_dependency_graph(source_path=source_path)
    G_undirected = graph.to_undirected()
    communities = nx_comm.greedy_modularity_communities(G=G_undirected)
    print(f"Detected {len(communities)} communities.")
    for i, community in enumerate(communities):
        print(f"Community {i+1} (size {len(community)}): {community}")


def analyse_path_length(
    source_path: Path,
) -> None:
    """
    Interpretation:
        A low average path length suggests a "small-world" structure, where
        models are reachable in few steps.

    """
    graph = build_dependency_graph(source_path=source_path)

    if nx.is_strongly_connected(G=graph):
        avg_path = nx.average_shortest_path_length(G=graph)
        print(f"Average shortest path length: {avg_path:.2f}")

    else:
        print("Graph is not strongly connected. Calculating for largest component...")
        largest_cc = max(nx.strongly_connected_components(G=graph), key=len)
        G_sub = graph.subgraph(largest_cc)
        avg_path = nx.average_shortest_path_length(G=G_sub)
        print(f"Average shortest path in largest SCC: {avg_path:.2f}")
