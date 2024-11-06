import tomllib
import os
from pathlib import Path
import networkx as nx
from pyvis.network import Network


def render_editable_network(graph: nx.MultiDiGraph, html_path: Path):
    """Save the graoph as html file."""
    nt = Network(height="500", width="90%", directed=True)
    # options for an editable graph
    nt.set_options("""
        const options = {
            "manipulation": {"enabled": true},
            "interaction": {"navigationButtons": true}
    }""")
    nt.from_nx(graph)
    print("Rendering:")
    nt.show(html_path.name, notebook=False)
    # no option to geive a full path to nt.show or nt.save_graph
    os.replace(Path(os.getcwd()) / html_path.name, html_path)


def read_graph_config(config_path: Path) -> dict:
    with open(config_path, "rb") as f:
        graph_config = tomllib.load(f)
    return graph_config


def color_nodes(
    graph: nx.MultiDiGraph,
    graph_config: dict,
    role: str = "orange",
    entity: str = "gray",
    opts: dict = {},
):
    for node in graph.nodes():
        if node in graph_config["nodes"]:
            if "type" not in graph_config["nodes"][node]:
                graph.add_node(opts.get("color", {}).get("default", "lightblue"))
            if graph_config["nodes"][node]["type"] == "role":
                graph.add_node(node, color=role)
            elif graph_config["nodes"][node]["type"] == "entity":
                graph.add_node(node, color=entity)


def add_graph_edges_from_config(
    graph: nx.MultiDiGraph, graph_config: dict, section: str
):
    graph.add_edges_from(graph_config[section]["edges"]["entities"], color="black")
    graph.add_edges_from(graph_config[section]["edges"]["entity_role"], color="black")
    for member in graph_config[section]["COLLABORATION"]["members"]:
        graph.add_edge("COLLABORATION", member, color="black")
    for n1, n2, label in graph_config[section]["edges"]["actions"]:
        graph.add_edge(n1, n2, label=label, color="orange")
