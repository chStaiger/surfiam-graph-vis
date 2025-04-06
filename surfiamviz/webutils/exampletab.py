"""Examples."""

import os
from pathlib import Path

import networkx as nx
import streamlit as st
import streamlit.components.v1 as components

from surfiamviz.graph_from_config import (
    add_graph_edges_from_config,
    import_example_graph,
)
from surfiamviz.utils import (
    color_edges,
    infer_coll_app_edges,
    read_graph_config,
)
from surfiamviz.webutils.utils import _set_attributes, _write_graph_to_file

repo_root = Path(os.path.realpath(__file__)).parent.parent.parent


def examples():
    """Examples tab."""
    st.title("SRAM example graphs")
    example_file = repo_root / "example_graphs/sram_examples.toml"
    if not example_file.is_file():
        st.write("Please make sure you downloaded the examples to example_graphs/sram_examples.toml.")
    example_graphs = import_example_graph(example_file)
    option = st.selectbox(
        "Choose a graph:",
        example_graphs.keys(),
        index=None,
    )
    config_file = repo_root / "configs/sram_config.toml"
    if not config_file.is_file():
        st.write("Please make sure you downloaded the config file to configs/sram_config.toml.")
    graph_config = read_graph_config(config_file)
    if option:
        ex_graph = nx.MultiDiGraph()
        add_graph_edges_from_config(ex_graph, example_graphs, option)
        _set_attributes(ex_graph, graph_config)
        infer_coll_app_edges(ex_graph, True)
        color_edges(ex_graph, graph_config)
        _write_graph_to_file(ex_graph, filename=repo_root / "gravis_html/example.html", scaling=True)
        with open(repo_root / "gravis_html/example.html", "r", encoding="utf-8") as htmlfile:
            components.html(htmlfile.read(), height=435)
        st.write(example_graphs[option]["explanation"])
