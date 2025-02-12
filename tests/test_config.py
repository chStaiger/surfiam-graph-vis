import pytest
import networkx as nx
from surfiamviz.graph_from_config import (
    add_graph_edges_from_config,
    set_node_type,
    set_node_levels_from_config
    )
from surfiamviz.utils import color_nodes, color_edges

graph  = nx.MultiDiGraph()

def test_config(config):
    assert "graph" in config

def test_add_graph_edges_from_config(config):
    assert "graph" in config

    add_graph_edges_from_config(graph, config, "graph")
    for edge in graph.edges:
        if edge[0] in ["ORGANISATION", "COLLABORATION"]:
            assert graph.get_edge_data(edge[0], edge[1]) == {0: {'edge_type': 'BACKBONE'}}
        elif edge[0] == "ORG_MANAGER":
            assert graph.get_edge_data(edge[0], edge[1]) == {0: {'edge_type': 'ACTIONS', 'label': 'create'}}
        elif edge[1] == "COLLABORATION":
            assert graph.get_edge_data(edge[0], edge[1]) == {0: {'edge_type': 'MEMBERS'}}
        elif edge[0] == "COLL_ADMIN" and edge[1] == "RESEARCHER":
            assert graph.get_edge_data(edge[0], edge[1]) == {0: {'edge_type': 'ACTIONS', 'label': 'invite'}}
        #print(edge[0], edge[1], graph.get_edge_data(edge[0], edge[1]))

def test_set_node_type(config):
    assert "node_types" in config

    set_node_type(graph, config)
    for node in graph:
        assert graph.nodes.get(node) == {'node_type': node}
        #print(node, graph.nodes.get(node))

def test_set_node_levels_from_config(config):
    set_node_levels_from_config(graph, config)
    for node in graph:
        assert "level" in graph.nodes.get(node)
        if node == "ORGANISATION":
            assert graph.nodes.get(node)["level"] == 1

def test_color_nodes(config):
    assert "node_colors" in config

    color_nodes(graph, config)
    for node in graph:
     assert "color" in graph.nodes.get(node)
     if node == "ORGANISATION":
        assert graph.nodes.get(node)["color"] == "gray"

def test_color_edges(config):
    assert "edge_colors" in config

    color_edges(graph, config)
    for edge in graph.edges:
        assert "color" in graph.get_edge_data(edge[0], edge[1], edge[2])
        if graph.get_edge_data(edge[0], edge[1], edge[2])["edge_type"] == "BACKBONE":
            assert graph.get_edge_data(edge[0], edge[1], edge[2])["color"] == "black"
