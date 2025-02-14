from surfiamviz.graph_from_sram_json import (
    get_nodes_from_dict,
    nodes_to_graph
)


def test_sram(sram):
    assert "collaborations" in sram


def test_get_nodes_from_dict(sram):
    nodes = get_nodes_from_dict(sram)
    assert nodes[0] == {"node_name": "FederFlow", "label": "federflow"}
    assert nodes[1] == ["Implementation Guidance", "Network Insights", "Strategy & Optimization"]
    for entry in nodes[2]:
        assert set(["node_name", "label", "edges_from", "services", "groups", "users"]).issubset(
            entry.keys()
        )
    for entry in nodes[3]:
        assert set(["admin_of", "create", "label", "created_by"]).issubset(nodes[3][entry].keys())


def test_nodes_to_graph(sram, config):
    nodes = get_nodes_from_dict(sram)
    graph = nodes_to_graph(nodes)
    #for edge in graph.edges:
    #    print(edge[0], edge[1], graph.get_edge_data(edge[0], edge[1]))
    node_types = []
    color_groups = []
    for node in graph:
        node_types.append(graph.nodes.get(node)["node_type"])
        if "color_group" in graph.nodes.get(node):
            color_groups.append(graph.nodes.get(node)["color_group"])
        #print(node, graph.nodes.get(node))
    assert set(node_types).issubset(config["node_types"].keys())
    node_type_labels = [config["node_types"][n]["name"] for n in config["node_types"]]
    assert set(color_groups).issubset(node_type_labels)
