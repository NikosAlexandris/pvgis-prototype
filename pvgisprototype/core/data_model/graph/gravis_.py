from pvgisprototype.core.factory.log import logger
import networkx as nx
from pathlib import Path
# import yaml
import gravis as gv
# from pvgisprototype.core.data_model.graph.colors import generate_color_from_path


# def add_gravis_metadata(graph, yaml_path):
#     """Enrich graph nodes with metadata for gravis visualization"""
#     # Load YAML data for detailed attributes
#     with open(yaml_path, 'r') as f:
#         yaml_data = yaml.safe_load(f)
    
#     for node in graph.nodes(data=True):
#         node_id = node[0]
#         node_data = node[1]
#         yaml_info = yaml_data.get(node_id, {})
        
#         # Create HTML content for hover and click
#         tooltip_html = f"""
#         <div style="font-family: Arial; padding: 5px; max-width: 300px;">
#             <h3 style="margin: 0 0 10px 0; color: #2c3e50;">{node_id}</h3>
#             <div><strong>Symbol:</strong> {yaml_info.get('symbol', '')}</div>
#             <div><strong>Unit:</strong> {yaml_info.get('unit', 'N/A')}</div>
#             <div><strong>Initial Value:</strong> {yaml_info.get('initial', 'N/A')}</div>
#             <hr style="margin: 10px 0;">
#             <div><em>{yaml_info.get('description', 'No description available')}</em></div>
#         </div>
#         """
        
#         # Add metadata that gravis will recognize
#         node[1]['metadata'] = {
#             'hover': tooltip_html,
#             'click': f"Detailed info for {node_id}",
#             'color': generate_color_from_path(node_id),  # Your existing color function
#             'size': 20 + len(list(graph.successors(node_id))) * 3  # Size based on dependencies
#         }
        
#     # Add edge labels from data 'label'
#     for u, v, data in graph.edges(data=True):
#         data['label'] = data.get('label', 'depends_on')


def assign_properties(
    g,
    node_size: int = 15,
):
    """
    Source of this function : https://robert-haas.github.io/gravis-docs/code/examples/external_tools/networkx.html#Example-2
    """
    logger.debug(f"Post-processing")
    # Centrality calculation
    # node_centralities = nx.eigenvector_centrality(g)
    node_centralities = nx.out_degree_centrality(g)
    logger.debug(f"{node_centralities=}")
    # edge_centralities = nx.edge_betweenness_centrality(g)

    # Community detection
    # communities = nx.algorithms.community.greedy_modularity_communities(g)

    # # Graph properties
    # g.graph["node_border_size"] = 1.5
    # g.graph["node_border_color"] = "white"
    # g.graph["edge_opacity"] = 0.9

    # Node properties: Size by centrality, shape by size, color by community
    # colors = [
    #     "red",
    #     "blue",
    #     "green",
    #     "orange",
    #     "pink",
    #     "brown",
    #     "yellow",
    #     "cyan",
    #     "magenta",
    #     "violet",
    # ]
    for node_id in g.nodes:
        node = g.nodes[node_id]
        node["size"] = node_size + node_centralities[node_id] * 33
        # node["shape"] = "octagon" if node["size"] > 30 else "circle"
        # for community_counter, community_members in enumerate(communities):
        #     if node_id in community_members:
        #         break
        # node["color"] = colors[community_counter % len(colors)]

    # # Edge properties: Size by centrality, color by community (within=community color, between=black)
    # for edge_id in g.edges:
    #     edge = g.edges[edge_id]
    #     source_node = g.nodes[edge_id[0]]
    #     target_node = g.nodes[edge_id[1]]
    #     edge["size"] = edge_centralities[edge_id] * 100
    #     edge["color"] = (
    #         source_node["color"]
    #         if source_node["color"] == target_node["color"]
    #         else "black"
    #     )


def visualise_gravis_d3(
    graph: nx.DiGraph,
    output_file: Path = Path("data_model_graph.html"),
    # node_size: int = 2400,
    # parent_node_size: int = 1200,
    # verbose: bool = False,
    # log_level: str = "WARNING",
    # log_file: Path | None = None,
    # rich_handler: bool = False,
):
    """
    """
    assign_properties(graph)
    fig = gv.d3(
        data=graph,
        graph_height=800,
        details_height=200,
        show_details=True,
        show_details_toggle_button=True,
        show_menu=True,
        show_menu_toggle_button=True,
        show_node=True,
        node_size_factor=1.2,
        node_size_data_source="size",
        use_node_size_normalization=False,
        node_size_normalization_min=10.0,
        node_size_normalization_max=50.0,
        node_drag_fix=True,
        node_hover_neighborhood=True,
        node_hover_tooltip=True,
        show_node_image=True,
        node_image_size_factor=1.0,
        show_node_label=True,
        show_node_label_border=True,
        node_label_data_source="label",
        node_label_size_factor=1.5,
        node_label_rotation=33.0,
        node_label_font="Arial",
        show_edge=True,
        edge_size_factor=1.0,
        edge_size_data_source="size",
        use_edge_size_normalization=True,
        edge_size_normalization_min=0.2,
        edge_size_normalization_max=5.0,
        edge_curvature=0.0,
        edge_hover_tooltip=True,
        show_edge_label=True,
        show_edge_label_border=True,
        edge_label_data_source="label",
        edge_label_size_factor=1.7,
        edge_label_rotation=33.0,
        edge_label_font="Arial",
        zoom_factor=0.9,
        large_graph_threshold=500,
        layout_algorithm_active=True,
        # specific for d3
        use_many_body_force=True,
        many_body_force_strength=-500.0,
        many_body_force_theta=0.9,
        use_many_body_force_min_distance=False,
        many_body_force_min_distance=10.0,
        use_many_body_force_max_distance=False,
        many_body_force_max_distance=1000.0,
        use_links_force=True,
        links_force_distance=150.0,
        links_force_strength=0.5,
        use_collision_force=True,
        collision_force_radius=90.0,
        collision_force_strength=0.9,
        use_x_positioning_force=False,
        x_positioning_force_strength=0.2,
        use_y_positioning_force=True,
        y_positioning_force_strength=0.5,
        use_centering_force=True,
    )

    # Export to HTML with embedded data
    fig.export_html(output_file)
    output_file.is_file()
