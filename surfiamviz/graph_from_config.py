"""Utility functions to draw networks."""

import networkx as nx


def set_node_type(graph: nx.MultiDiGraph, graph_config: dict):
    """Add the type to each node in the graph.

    Only used for graphs rendered from the config file.

    The function looks up the node type of a node in the configuration doictionary
    by mapping each of the defined node_types as a prefix to the node.
    The first one that matches defines the node type.
    """
    config_node_types = graph_config["node_types"].keys()
    for node in graph.nodes():
        if "node_type" not in graph.nodes.get(node):
            res = [node_type for node_type in config_node_types if node_type in node]
            if len(res) == 0:
                print(f"WARNING Cannot retrieve the type of {node} from the config.")
                ntype = ""
            elif len(res) > 1:
                print(f"WARNING {node} can be of types {res}. Setting type to {res[0]}.")
                ntype = res[0]
            else:
                ntype = res[0]
            graph.add_node(node, node_type=ntype)


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


def add_graph_edges_from_config(graph: nx.MultiDiGraph, graph_config: dict, section: str):
    """Add the edges from a graph section in the config file."""
    for _, edge_set in graph_config[section].items():
        etype = edge_set["type"]
        for edge in edge_set["edges"]:
            if len(edge) == 2:
                graph.add_edge(edge[0], edge[1], edge_type=etype)
            elif len(edge) == 3:
                graph.add_edge(edge[0], edge[1], edge_type=etype, label=edge[2])
            else:
                print(f"WARNING Something is wrong with {edge}. Expect [u, v, label].")
