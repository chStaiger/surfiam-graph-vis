from pathlib import Path
import networkx as nx

from utils import (
    read_graph_config,
    color_nodes,
    render_editable_network,
    add_graph_edges_from_config,
)

# Configuration file
PATH = Path.absolute(Path(__file__)).parent
config_path = PATH.parent / "configs" / "graph_config.toml"
print(PATH)
print(config_path)
graph_config = read_graph_config(config_path)

graph = nx.MultiDiGraph()
# add edges of the graph indicated by section "plain_graph"
add_graph_edges_from_config(graph, graph_config, "plain_graph")

# color nodes according to their type
color_nodes(graph, graph_config)

# render html
html_path = PATH.parent / "html" / "plain_graph.html"
render_editable_network(graph, html_path)
