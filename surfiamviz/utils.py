"""Utility functions to draw networks."""

import os
from pathlib import Path
from pprint import pprint

import networkx as nx
import tomllib
from pyvis.network import Network


def render_editable_network(graph: nx.MultiDiGraph, html_path: Path, debug: bool = False):
    """Save the graph as html file."""
    nt = Network(height="750", width="90%", directed=True, filter_menu=True)
    # nt.show_buttons()
    # options for an editable graph
    nt.set_options("""
        const options = {
            "manipulation": {"enabled": true},
            "interaction": {"navigationButtons": true},
            "physics": {"enabled": false, "minVelocity": 0.75},
            "edges": {"smooth": true},
            "layout": {
                "hierarchical": {
                    "enabled": true,
                    "direction": "LR",
                    "sortMethod": "directed"
                }
            }
    }""")
    nt.from_nx(graph)
    if debug:
        pprint(nt.edges)
        pprint(nt.nodes)
    print(f"Rendering {html_path}:")
    nt.show(html_path.name, notebook=False)
    # no option to geive a full path to nt.show or nt.save_graph
    os.replace(Path(os.getcwd()) / html_path.name, html_path)


def read_graph_config(config_path: Path) -> dict:
    """Read config file."""
    with open(config_path, "rb") as f:
        graph_config = tomllib.load(f)
    return graph_config


def color_nodes(graph: nx.MultiDiGraph, graph_config: dict):
    """Add the node attribute color to the nodes.

    The function expects the graph to be annotated with node_type which should
    correspond to the section node_types in the config file.
    Optionally the nodes can also be annotated with color_group which will be
    translated to the color as defined in the section node_colors in the config file..

    Parameters
    ----------
    graph: MultiDiGraph
        The graph rendered from a SRAM export or a section in the configuration file.
    graph_config: dict
        The configuration file

    """
    default_color = graph_config["node_colors"].get("default", "lightblue")
    for node in graph.nodes():
        node_attrs = graph.nodes.get(node)
        if "color_group" in node_attrs:
            color_group = node_attrs.get("color_group", "default")
        elif "node_type" in node_attrs:
            if node_attrs["node_type"] in graph_config["node_types"]:
                color_group = graph_config["node_types"][node_attrs["node_type"]].get(
                    "name", "default"
                )
            else:
                color_group = "default"
        else:
            color_group = "default"
        node_color = graph_config["node_colors"].get(color_group, default_color)
        graph.add_node(node, color=node_color)


def color_edges(graph: nx.MultiDiGraph, graph_config: dict):
    """Add the attribute color to edges.

    The functions expects the edges of a graph to be annotated with edge_type which should
    correspond to the edges defined in the setiction edge_colors in the config file.
    """
    for edge in graph.edges:
        etype = graph[edge[0]][edge[1]][edge[2]].get("edge_type", "default")
        edge_color = graph_config["edge_colors"][etype]
        graph[edge[0]][edge[1]][edge[2]]["color"] = edge_color
