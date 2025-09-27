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
import matplotlib.pyplot as plt
import networkx as nx
from pvgisprototype.core.factory.log import logger


def visualise_circular_tree(
    graph: nx.DiGraph,
    output_file: str = "data_model_dependency_graph",
    node_size: int = 20,
) -> None:
    """ """
    pos = nx.nx_agraph.graphviz_layout(
        G=graph,
        prog="twopi",
        args="",
    )

    # plt.figure(figsize=(11.69, 11.69))
    plt.figure(figsize=(10, 10))
    nx.draw(
        G=graph,
        pos=pos,
        node_size=node_size,
        alpha=0.5,
        node_color="blue",
        with_labels=False,
    )

    leaf_nodes = [n for n in graph.nodes if graph.out_degree(n) == 0]

    # leaf_nodes = set()
    # parent_nodes = set()
    # parent_paths = {}

    # for u, v, data in graph.edges(data=True):
    #     leaf_nodes.add(u)
    #     parent_nodes.add(v)
    #     parent_paths[v] = data.get('label', 'unknown')

    logger.info(
        "Leaf nodes\n\n{leaf_nodes}",
        # "Leaf nodes\n\n{leaf_nodes}\n\nParent nodes\n\n{parent_nodes}",
        leaf_nodes=leaf_nodes,
        # parent_nodes=parent_nodes,
    )

    # Create labels only for leaf nodes
    # labels = {n: str(n) for n in leaf_nodes}
    labels = {
        # n: n + f"\n{data.get('symbol', '')}"
        node: f"{data.get('symbol', 'Symbol')}"
        for node, data in graph.nodes(data=True)
        if node in leaf_nodes
    }

    # Draw labels for leaf nodes
    nx.draw_networkx_labels(
        G=graph,
        pos=pos,
        labels=labels,
        font_size=7,
        font_color="red",
        # font_weight="bold",
        horizontalalignment='center'
    )

    # Titles
    plt.suptitle(
        t="Data Model Dependency Graph ⎄",
        fontsize=12,
        fontweight='bold',
        color='#2F3131',  #darkgray',
    )

    # plt.title(
    #     label="Lighter Colors = Path Hierarchy | Salmon = Leaf Node",
    #     fontsize=9,
    #     color='#2F4F4F',  #'darkgray',
    #     # pad=10
    # )

    # plt.axis("off")
    plt.axis("equal")
    # plt.tight_layout(rect=[0, 0, 1, 0.98])

    # Save
    output_file += ".png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Graph saved to {output_file}")
