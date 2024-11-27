#!/usr/bin/env python3
"""Draw the plain sram graph."""

from pathlib import Path
import networkx as nx

from sramviz.utils import (
    read_graph_config,
    color_nodes,
    render_editable_network,
    add_graph_edges_from_config,
    set_node_levels_from_config,
    set_node_type,
)

from sramviz.graph_from_sram_json import read_json, get_nodes_from_dict, nodes_to_graph

RENDER_JSON = True
RENDER_SECTION = "all_nodes_graph"

# Configuration file
PATH = Path.absolute(Path(__file__)).parent
config_path = PATH.parent / "configs" / "graph_config.toml"
graph_config = read_graph_config(config_path)

colors = {
    "group": "darkorange",
    "service": "teal",
    "default": "lightblue",
    "user": "darkseagreen",
}

# SRAM json export file
if RENDER_JSON:
    sram_json_path = PATH.parent / "data" / "output.json"
    sram_dict = read_json(sram_json_path)

    # Draw graph from sram json file
    nodes = get_nodes_from_dict(sram_dict)
    graph = nodes_to_graph(nodes)
    color_nodes(graph, graph_config, **colors)

    # render html
    html_path = PATH.parent / "html" / "exported_graph.html"
    render_editable_network(graph, html_path)

# Draw graph section from config
if RENDER_SECTION:
    graph = nx.MultiDiGraph()

    # add edges of the graph indicated by section
    add_graph_edges_from_config(graph, graph_config, RENDER_SECTION)
    set_node_type(graph, graph_config)
    set_node_levels_from_config(graph, graph_config)
    color_nodes(graph, graph_config, **colors)

    # render html
    html_path = PATH.parent / "html" / f"{RENDER_SECTION}.html"
    render_editable_network(graph, html_path)
