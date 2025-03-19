"""Utility functions to draw networks."""

import itertools
from pathlib import Path

import gravis as gv
import networkx as nx
import tomllib


def render_editable_network(graph: nx.MultiDiGraph, html_path: Path, scale_nodes=True):
    """Save the graph as html file."""
    print(f"Rendering {html_path}:")

    # fix hierarchical positioning of node
    max_deg = max(deg for _, deg in graph.to_undirected().degree)
    scaling = 300 + len(graph.nodes()) * max_deg

    pos = nx.drawing.layout.multipartite_layout(graph, scale=scaling)
    for name, (x, y) in pos.items():
        node = graph.nodes[name]
        node["x"] = x
        node["y"] = y
    print(scale_nodes)
    if scale_nodes is True:
        print("blabla")
        deg_centrality = dict(graph.to_undirected().degree)
        _ = [graph.add_node(node, size=25 + deg_centrality[node]) for node in graph.nodes()]

    fig = gv.vis(
        graph,
        show_edge_label=True,
        edge_label_data_source="label",
        edge_curvature=0.3,
        use_node_size_normalization=False,
        node_size_data_source="size",
        layout_algorithm_active=False,
        show_details=True,
    )
    fig.export_html(html_path)

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


def infer_coll_app_edges(graph: nx.MultiDiGraph, verbose):
    """Infer the relationship between an app and a collaboration.

    Whether a collaboration can be connected to an application depends on the organisation
    admin approving the application and an application admin approving a collaboration.
    Those can be infered from the action edges "appoves" and "disapproves".
    """
    org_adms = [n for n in graph.nodes if graph.nodes.get(n)["node_type"] == "ORG_ADMIN"]
    app_adms = [n for n in graph.nodes if graph.nodes.get(n)["node_type"] == "APP_ADMIN"]
    apps = [n for n in graph.nodes if graph.nodes.get(n)["node_type"] == "APPLICATION"]
    colls = [n for n in graph.nodes if graph.nodes.get(n)["node_type"] == "COLLABORATION"]

    approved_by_app = [
        (coll, adm, app)
        for (coll, adm, app) in itertools.product(colls, app_adms, apps)
        if graph.has_edge(adm, coll)
        and graph.has_edge(app, adm)
        and graph.get_edge_data(adm, coll)[0]["edge_type"] == "ACTIONS"
        and graph.get_edge_data(adm, coll)[0]["label"] == "approves"
    ]
    approved_by_org = [
        (a, o)
        for a, o in itertools.product(apps, org_adms)
        if graph.has_edge(o, a)
        and graph.get_edge_data(o, a)[0]["edge_type"] == "ACTIONS"
        and graph.get_edge_data(o, a)[0]["label"] == "approves"
    ]

    for coll, org_adm, app, app_adm in itertools.product(colls, org_adms, apps, app_adms):
        # a collaboration belongs to an org_admin if there exists a path which only contains
        # collaboration -> organisation -> orgadmin
        # collaboration -> unit -> organisation -> orgadmin
        paths = [
            sorted(["COLLABORATION", "ORGANISATION", "ORG_ADMIN"]),
            sorted(["COLLABORATION", "ORGANISATION", "ORG_ADMIN", "UNIT"]),
        ]

        all_paths = nx.all_simple_paths(graph.to_undirected(), coll, org_adm)
        valid_paths = []
        for path in all_paths:
            node_types = [graph.nodes.get(n)["node_type"] for n in path]
            if sorted(node_types) in paths:
                valid_paths.append(path)
        if verbose:
            print(coll, org_adm, app, app_adm, "valid paths: ", valid_paths)
        if len(valid_paths) > 0:
            # we choose >0 since there might also be trust and other action edges
            # which results in multiple paths, we are also working with multigraphs here.
            if (coll, app_adm, app) in approved_by_app:
                if verbose:
                    print("Approved:", coll, app_adm, app)
                if (app, org_adm) in approved_by_org:
                    if verbose:
                        print("Approved:", app, org_adm)
                    graph.add_edge(coll, app, edge_type="BACKBONE")
                else:
                    if verbose:
                        print("Not Approved:", app, org_adm)
                    graph.add_edge(coll, app, edge_type="REJECT", label="reject by org")
            else:
                if verbose:
                    print("Not Approved:", coll, app_adm, app)
                graph.add_edge(coll, app, edge_type="REJECT", label="reject by app")
        if verbose:
            print("------")

def subgraph(graph: nx.MultiDiGraph, edge_types: list, node_types: list) -> nx.MultiDiGraph:
    """Define a subgraph by node_types and edge_types."""
    selected_nodes = []
    for node in graph.nodes():
        node_attrs = graph.nodes.get(node)
        if "node_type" in node_attrs and node_attrs["node_type"] in node_types:
            selected_nodes.append(node)
    selected_edges = []
    for edge in graph.edges:
        if "edge_type" in graph[edge[0]][edge[1]][edge[2]] and graph[edge[0]][edge[1]][edge[2]]["edge_type"] in edge_types:
            selected_edges.append(edge)
    subgraph = graph.subgraph(selected_nodes)
    return subgraph
            
