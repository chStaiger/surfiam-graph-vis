"""Utility functions to draw networks."""

import os
from pathlib import Path

import networkx as nx
import tomllib
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
    print(f"Rendering {html_path}:")
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
    """Add the node attribute color to the nodes.

    The function expects the graph to be annotated with node_type which should
    correspond to the node_types in the graph_config.
    Optionally the nodes can also be annotated with color_group which will be
    translated to the color of entity, rol or as defined in kwargs.

    Parameters
    ----------
    graph: MultiDiGraph
        The graph rendered from a SRAM export or a section in the configuration file.
    graph_config: dict
        The configuration file
    role:
        Predefined color for node type role.
    entity:
        Predefined color for node type entity.
    kwargs:
        A mapping from color_group to the actual color. E.g. {"user": "blue"}
        You can also overwrite the default settings of role and entity with kwargs.

    """
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

    Only used for graphs rendered from the config file.

    The function looks up the node type of a node in the configuration doictionary
    by mapping each of the defined node_types as a prefix to the node.
    The first one that matches defined the node type.
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
    """Set the level of the node in the graph hierarchy to the level defined in graph_config.

    Only used for graphs from the config file.

    Nodes are expected to carry the a label node_type. this needs to correspond to one of
    the node_types in graph_config. The function sets the level of a node to the number
    found in the configuration
    """
    for node in graph.nodes():
        node_attrs = graph.nodes.get(node)
        if "level" not in node_attrs:
            if "node_type" in node_attrs:
                ntype = node_attrs["node_type"]
                lvl = graph_config["node_types"][ntype]["level"]
                graph.add_node(node, level=lvl)
            else:
                print(f"WARNING {node} is not labeled with its node_type. Cannot set level.")


def add_graph_edges_from_config(
    graph: nx.MultiDiGraph, graph_config: dict, section: str
):
    """Add the edges from a graph section in the config file and add the color label to the edge.

    Default edge color is lightblue. The colors need to be defined in the section edge_types
    in the configuration.
    """
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
