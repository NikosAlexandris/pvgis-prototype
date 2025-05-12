from graphviz import Digraph
import networkx as nx
import matplotlib.pyplot as plt
from pvgisprototype.core.data_model.visualise.colors import generate_color_from_path
from pvgisprototype.core.factory.log import logger


def visualize_graph(
    graph: dict,
    output_file: str = "data_model_dependency_graph"
) -> None:
    """
    Visualize a graph with parent nodes in green using networkx and
    matplotlib
    """
    G = nx.DiGraph()

    # Collect nodes (parents appearing in any 'require' list)
    leaf_nodes = set()
    parent_nodes = set()
    parent_paths = {}

    for leaf, parents in graph.items():
        leaf_nodes.add(leaf)
        for parent, path in parents:
            parent_nodes.add(parent)
            parent_paths[parent] = path

    # Assign node colors
    node_colors = {}
    for node in leaf_nodes:
        node_colors[node] = "salmon"

    for name, path in parent_paths.items():  # name == (of ) parent (node !)
        node_colors[name] = generate_color_from_path(path)

    # Add nodes
    for node in leaf_nodes.union(parent_nodes):
        G.add_node(
            node_for_adding=node,
            label=node,
        )
    node_colors_list = [node_colors[node] for node in G.nodes]
    node_sizes = [1430 if node in parent_nodes else 2400 for node in G.nodes]

    # Add edges
    for child, parents in graph.items():
        for parent, path in parents:
            G.add_edge(
                u_of_edge=child,
                v_of_edge=parent,
                # weight=0.2,
                label=path,
            )

    # Layout
    plt.figure(figsize=(11.69,8.27))  # landscape
    position = nx.spring_layout(
        G=G,
        seed=42,
        k=.7,  # k controls spacing
        # weight='weight',
    )

    # Draw nodes
    nx.draw(
        G=G,
        pos=position,
        with_labels=False,
        node_size=node_sizes,
        node_color=node_colors_list,
        edge_color='lightgray',
        width=0.5,
        # alpha=0.95,
        alpha=0.7,
        linewidths=0.5,
        # edgecolors='black',
        ax=plt.gca()
    )

    # Draw node labels
    parent_labels = {n: n for n in G.nodes if n in parent_nodes}
    leaf_labels = {n: n for n in G.nodes if n in leaf_nodes}

    # Offset parent labels slightly for readability
    # label_pos_offset = {k: (v[0], v[1] + 0.02) for k, v in pos.items()}

    nx.draw_networkx_labels(
        G=G,
        # pos=label_pos_offset,
        pos=position,
        labels=parent_labels,
        font_size=7,
        font_color='gray',
        font_weight='normal',
        horizontalalignment='center',
        verticalalignment='bottom',
        ax=plt.gca()
    )
    nx.draw_networkx_labels(
        G=G,
        pos=position,
        labels=leaf_labels,
        font_size=8,
        font_color='darkgray',
        font_weight='bold',
        horizontalalignment='center',
        verticalalignment='top',
        ax=plt.gca()
    )

    # Draw edge labels
    edge_labels = {(u, v): G.edges[u, v]['label'] for u, v in G.edges() }
    nx.draw_networkx_edge_labels(
        G=G,
        pos=position,
        edge_labels=edge_labels,
        font_size=6,
        font_color="blue",
        alpha=0.66,
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1.5),
        label_pos=0.66,
        ax=plt.gca()
    )

        # Step 8: Title and layout
    plt.suptitle(
        t="Data Model Dependency Graph",
        fontsize=12,
        fontweight='bold',
        color='darkgray',
    )
    plt.title(
        label="Lighter Colors = Path Hierarchy | Salmon = Leaf Node",
        fontsize=9,
        color='darkgray',
        # pad=10
    )
    plt.axis('off')
    plt.tight_layout(pad=0, rect=[0, 0, 0, 0.98])  # Leave space at the top

    # Save the graph to a file
    output_file += ".png"
    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight",
        transparent=False,
        facecolor='white'
    )
    plt.close()
    logger.info(f"Graph saved to {output_file}")


def visualize_hierarchical_graph(graph: dict, output_file: str = "hierarchical_graph"):
    """Visualize with hierarchical layout using graphviz"""
    dot = Digraph(
        comment="Hierarchical Data Model Dependencies",
        graph_attr={"rankdir": "LR", "splines": "ortho"},
    )

    # Add nodes with color coding
    parent_nodes = set()
    for deps in graph.values():
        parent_nodes.update(deps)

    for node in graph:
        dot.node(
            node,
            label=node,
            _attributes={
                "style": "filled",
                "fillcolor": "lightgreen" if node in parent_nodes else "salmon",
                "shape": "box",
                "width": "1.5" if node in parent_nodes else "1.2",
            },
        )

    # Add edges
    for node, deps in graph.items():
        for dep in deps:
            dot.edge(node, dep)

    dot.render(output_file, format="png", cleanup=True)
    print(f"Hierarchical graph saved to {output_file}.png")
