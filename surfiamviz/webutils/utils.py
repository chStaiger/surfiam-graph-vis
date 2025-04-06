"""Utils for the web app."""

from pathlib import Path

from surfiamviz.graph_from_config import (
    set_node_levels_from_config,
    set_node_type,
)
from surfiamviz.graph_from_sram_json import (
    get_nodes_from_dict,
    nodes_to_graph,
)
from surfiamviz.utils import (
    color_edges,
    color_nodes,
    render_editable_network,
)


def _load_graph(s_dict):
    nodes = get_nodes_from_dict(s_dict)
    g = nodes_to_graph(nodes)
    return g


def _set_attributes(g, g_config):
    set_node_type(g, g_config)
    set_node_levels_from_config(g, g_config)
    color_nodes(g, g_config)
    color_edges(g, g_config)


def _write_graph_to_file(g, filename="gravis_html/streamlit_graph.html", scaling=True):
    if Path(filename).exists():
        Path(filename).unlink()
    render_editable_network(g, filename, scaling)
