import tomllib
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path


# Configuration file
config_path = "graph_config.toml"

with open(config_path, "rb") as f:
    graph_config = tomllib.load(f)

graph = nx.MultiGraph()

graph.add_edges_from(graph_config["plain_graph"]["edges"]["entities"], color="b")
graph.add_edges_from(graph_config["plain_graph"]["edges"]["entity_role"], color="b")
for member in graph_config["plain_graph"]["COLLABORATION"]["members"]:
    graph.add_edge("COLLABORATION", member, color="b")
graph.add_edges_from(graph_config["plain_graph"]["edges"]["actions"], color="r")

pos = nx.spring_layout(graph)
edges = graph.edges()
colors = [graph[u][v][0]['color'] for u,v in edges]
nx.draw(graph, pos, with_labels = True, edge_color=colors)
plt.show()
