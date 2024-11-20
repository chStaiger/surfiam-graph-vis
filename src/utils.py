"""Utility functions to draw networks."""

import tomllib
import os
from pathlib import Path
import networkx as nx
from pyvis.network import Network


def render_editable_network(graph: nx.MultiDiGraph, html_path: Path):
    """Save the graph as html file."""
    nt = Network(height="500", width="90%", directed=True)
    # nt.show_buttons()
    # options for an editable graph
    nt.set_options("""
        const options = {
            "manipulation": {"enabled": true},
            "interaction": {"navigationButtons": true},
            "physics": {"enabled": false, "minVelocity": 0.75},
            "edges": {"smooth": false}
    }""")
    nt.from_nx(graph)
    print("Rendering:")
    nt.show(html_path.name, notebook=False)
    # no option to geive a full path to nt.show or nt.save_graph
    os.replace(Path(os.getcwd()) / html_path.name, html_path)


def read_graph_config(config_path: Path) -> dict:
    """Read config file."""
    with open(config_path, "rb") as f:
        graph_config = tomllib.load(f)
    return graph_config


def color_nodes(
    graph: nx.MultiDiGraph,
    graph_config: dict,
    role: str = "orange",
    entity: str = "gray",
    **kwargs,
):
    """Color nodes according to their type in the config file."""
    default = kwargs.get("default", "lightblue")
    for node in graph.nodes():
        if "node_type" in graph.nodes.get(node):
            node_type = graph.nodes.get(node)["node_type"]
        elif node in graph_config["nodes_types"]:
            node_type = graph_config["nodes_types"][node].get("type", "default")
        else:
            node_type = "default"
        if node_type == "role":
            graph.add_node(node, color=role)
        elif node_type == "entity":
            graph.add_node(node, color=entity)
        elif node_type in kwargs:
            graph.add_node(node, color=kwargs[node_type])
        else:
            graph.add_node(node, color=default)


def add_graph_edges_from_config(
    graph: nx.MultiDiGraph, graph_config: dict, section: str
):
    """Add the edges from a section in the config file."""
    graph.add_edges_from(graph_config[section]["edges"]["entities"], color="black")
    graph.add_edges_from(graph_config[section]["edges"]["entity_role"], color="black")
    for member in graph_config[section]["COLLABORATION"]["members"]:
        graph.add_edge("COLLABORATION", member, color="black")
    for n1, n2, label in graph_config[section]["edges"]["actions"]:
        graph.add_edge(n1, n2, label=label, color="orange")
