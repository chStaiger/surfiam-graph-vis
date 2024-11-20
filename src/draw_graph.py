"""Draw the plain sram graph."""

from pathlib import Path
import networkx as nx

from utils import (
    read_graph_config,
    color_nodes,
    render_editable_network,
    add_graph_edges_from_config,
)

from graph_from_sram_json import read_json, get_nodes_from_dict, nodes_to_graph

# Configuration file
PATH = Path.absolute(Path(__file__)).parent
config_path = PATH.parent / "configs" / "graph_config.toml"
graph_config = read_graph_config(config_path)

# SRAM json export file
sram_json_path = PATH.parent / "data" / "output.json"
sram_dict = read_json(sram_json_path)

colors = {
    "group": "darkorange",
    "service": "teal",
    "default": "lightblue"
}

# Draw graph from sram json file
nodes = get_nodes_from_dict(sram_dict)
graph = nodes_to_graph(nodes)

color_nodes(graph, graph_config, **colors)

# render html
html_path = PATH.parent / "html" / "exported_graph.html"
render_editable_network(graph, html_path)


# Draw standard graph
graph = nx.MultiDiGraph()
# add edges of the graph indicated by section "plain_graph"
add_graph_edges_from_config(graph, graph_config, "plain_graph")

# color nodes according to their type
color_nodes(graph, graph_config, **colors)

# render html
html_path = PATH.parent / "html" / "plain_graph.html"
render_editable_network(graph, html_path)
