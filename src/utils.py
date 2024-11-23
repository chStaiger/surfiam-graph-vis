"""Utility functions to draw networks."""

import tomllib
import os
from pathlib import Path
import networkx as nx
from pyvis.network import Network


def render_editable_network(graph: nx.MultiDiGraph, html_path: Path):
    """Save the graph as html file."""

    nt = Network(height="750", width="90%", directed=True)
    # nt.show_buttons()
    # options for an editable graph
    nt.set_options("""
        const options = {
            "manipulation": {"enabled": true},
            "interaction": {"navigationButtons": true},
            "physics": {"enabled": false, "minVelocity": 0.75},
            "edges": {"smooth": false},
            "layout": {
                "hierarchical": {
                    "enabled": true,
                    "direction": "LR",
                    "sortMethod": "directed"
                }
            }
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
        node_attrs = graph.nodes.get(node)
        if "color_group" in node_attrs:
            color_group = node_attrs["color_group"]
        elif node_attrs["node_type"] in graph_config["node_types"]:
            color_group = graph_config["node_types"][node].get("type", "default")
        else:
            color_group = "default"
        if color_group == "role":
            graph.add_node(node, color=role)
        elif color_group == "entity":
            graph.add_node(node, color=entity)
        elif color_group in kwargs:
            graph.add_node(node, color=kwargs[color_group])
        else:
            graph.add_node(node, color=default)


def set_node_type(graph: nx.MultiDiGraph, graph_config: dict):
    """Add the type to each node in the graph.
    Only used for graphs from the config file.
    """
    node_types = graph_config["node_types"].keys()
    for node in graph.nodes():
        if "node_type" not in graph.nodes.get(node):
            res = [node_type for node_type in node_types if node_type in node]
            color_group = "default"
            if len(res) == 0:
                print(f"WARNING Cannot retrieve the type of {node} from the config.")
                ntype = ""
            elif len(res) > 1:
                print(
                    f"WARNING {node} can be of types {res}. Setting type to {res[0]}."
                )
                ntype = res[0]
                color_group = graph_config["node_types"][ntype]["type"]
            else:
                ntype = res[0]
                color_group = graph_config["node_types"][ntype]["type"]
            graph.add_node(node, node_type=ntype, color_group=color_group)


def set_node_levels_from_config(graph: nx.MultiDiGraph, graph_config: dict):
    """Set the level of the node in the graph hierarchy.
    Only used for graphs from the config file.
    """
    for node in graph.nodes():
        node_attrs = graph.nodes.get(node)
        if "level" not in node_attrs:
            if "node_type" in node_attrs:
                ntype = node_attrs["node_type"]
                lvl = graph_config["node_types"][ntype]["level"]
                graph.add_node(node, level=lvl)


def add_graph_edges_from_config(
    graph: nx.MultiDiGraph, graph_config: dict, section: str
):
    """Add the edges from a section in the config file."""
    for _, edge_set in graph_config[section].items():
        # defaults for edges
        color = "lighblue"  # default color, indicating edge color is not defined
        label = ""  # label of the edge, only necessary for actions and members
        etype = edge_set["type"]
        if etype in graph_config["edge_types"]:
            color = graph_config["edge_types"][etype].get("color", "lightblue")
        else:
            print(f"INFO: {etype} not found in config section 'edge_types'.")
            color = "lightblue"
        if "label" in graph_config["edge_types"][etype]:
            label = graph_config["edge_types"][etype]["label"]

        for edge in edge_set["edges"]:
            if len(edge) == 2:
                graph.add_edge(edge[0], edge[1], color=color, label=label)
            elif len(edge) == 3:
                graph.add_edge(edge[0], edge[1], color=color, label=edge[2])
            else:
                print(f"WARNING Something is wrong with {edge}. Expect [u, v, label].")
