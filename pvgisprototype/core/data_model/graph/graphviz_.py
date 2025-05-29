import networkx as nx
import matplotlib.pyplot as plt
from pvgisprototype.core.data_model.graph.colors import generate_color_from_path
from pvgisprototype.core.factory.log import logger
from networkx.drawing.nx_agraph import graphviz_layout

from matplotlib import font_manager, rcParams


# Add the font path
noto_sans_math_font_path = "/usr/share/fonts/noto/NotoSansMath-Regular.ttf"
font_manager.fontManager.addfont(noto_sans_math_font_path)
rcParams['font.family'] = 'Noto Sans Math'


def visualise_graph(
    graph: nx.DiGraph,
    output_file: str = "data_model_dependency_graph",
    node_size: int = 2400,
    parent_node_size: int = 1200,
) -> None:
    """
    Visualize a dependency graph with hierarchical layout
    """
    leaf_nodes = set()
    parent_nodes = set()
    parent_paths = {}

    for u, v, data in graph.edges(data=True):
        leaf_nodes.add(u)
        parent_nodes.add(v)
        parent_paths[v] = data.get('label', 'unknown')

    logger.info(
        "Leaf nodes\n\n{leaf_nodes}\n\nParent nodes\n\n{parent_nodes}",
        leaf_nodes=leaf_nodes,
        parent_nodes=parent_nodes,
    )

    # Assign node colors
    node_colors = {}

    # Color leaf nodes
    for node in leaf_nodes:
        node_colors[node] = "salmon"

    # Color parent nodes based on path
    for name, path in parent_paths.items():
        node_colors[name] = generate_color_from_path(path)

    # Ensure all nodes have a color
    for node in graph.nodes:
        if node in leaf_nodes:
            node_colors[node] = "salmon"
        elif node in parent_nodes:
            path = parent_paths.get(node, "unknown")
            node_colors[node] = generate_color_from_path(path)
        else:
            # Isolated node (no incoming or outgoing edges)
            node_colors[node] = "salmon"  # Default to leaf

    # Node sizes
    node_sizes = [
        parent_node_size if node in parent_nodes else node_size for node in graph.nodes
    ]

    # Use graphviz_layout for hierarchical layout
    plt.figure(figsize=(32, 11.69))
    # plt.figure(figsize=(11.69,8.27))  # landscape
    position = graphviz_layout(
        G=graph,
        # prog='sfdp',
        # args="-Goverlap=prism100 -Gsep=0.1",
        # prog="dot",  # Use `dot` for top-down hierarchy
        # args="-Granksep=1.5 -Gnodesep=1.0",
        prog='twopi',
        args="-Groot=node_name -Gsize=20 -Gsep=1",
    )
    # position = nx.spring_layout(
    #     G=graph,
    #     seed=42,
    #     k=.7,  # k controls spacing
    #     # weight='weight',
    # )

    # Draw nodes
    nx.draw(
        G=graph,
        pos=position,
        with_labels=False,
        node_size=node_sizes,
        node_color=[node_colors[n] for n in graph.nodes],
        edge_color='lightgray',
        width=0.5,
        alpha=0.7,
        linewidths=0.5,
        # edgecolors='black',
        ax=plt.gca()
    )

    # Draw labels
    # Parent labels excluding nodes that are also leaf nodes
    parent_labels = {
        n: n + f"\n{data.get('symbol', '')}"
        for n in parent_nodes
        if n not in leaf_nodes
    }
    leaf_labels = {
        n: n + f"\n{data.get('symbol', '')}"
        for n, data in graph.nodes(data=True)
        if n in leaf_nodes
    }

    label_pos = {k: (v[0], v[1] + 0.02) for k, v in position.items()}
    # node_symbols = {n: data.get("symbol", "") for n, data in graph.nodes(data=True)}

    nx.draw_networkx_labels(
        G=graph,
        pos=label_pos,
        labels=parent_labels,
        font_size=9,
        font_color="#4D4D4D",  # Gray 30
        font_weight="normal",
        horizontalalignment='center',
        # verticalalignment='bottom',
        ax=plt.gca()
    )
    nx.draw_networkx_labels(
        G=graph,
        pos=position,
        # labels=leaf_labels,
        labels=leaf_labels,
        font_size=10,
        font_color="#666666",
        # font_color='darkgray',
        font_weight='bold',
        horizontalalignment='center',
        # verticalalignment='top',
        ax=plt.gca()
    )

    # Draw edge labels
    edge_labels = {(u, v): data["label"] for u, v, data in graph.edges(data=True)}
    nx.draw_networkx_edge_labels(
        G=graph, 
        pos=position,
        edge_labels=edge_labels,
        font_size=8,
        font_color='blue',
        alpha=0.66,
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1.5),
        label_pos=0.66,
        ax=plt.gca()
    )

    # Titles
    plt.suptitle(
        t="Data ⎄ Model Dependency Graph ⎄",
        fontsize=12,
        fontweight='bold',
        color='#2F3131',  #darkgray',
    )
    plt.title(
        label="Lighter Colors = Path Hierarchy | Salmon = Leaf Node",
        fontsize=9,
        color='#2F4F4F',  #'darkgray',
        # pad=10
    )
    plt.axis("off")
    plt.tight_layout(rect=[0, 0, 1, 0.98])

    # Save
    output_file += ".png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Graph saved to {output_file}")


def visualise_hierarchical_graph(graph: dict, output_file: str = "hierarchical_graph"):
    """Visualize with hierarchical layout using graphviz"""
    dot = nx.DiGraph(
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
