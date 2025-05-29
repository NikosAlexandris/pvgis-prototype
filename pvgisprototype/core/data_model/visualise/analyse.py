
import networkx as nx

def basic_metrics(G):
    print(f"Number of nodes (models): {G.number_of_nodes()}")
    print(f"Number of edges (dependencies): {G.number_of_edges()}")
    print(f"Graph density: {nx.density(G):.4f}")
    print(f"Is the graph a DAG (Directed Acyclic Graph)? {nx.is_directed_acyclic_graph(G)}")
