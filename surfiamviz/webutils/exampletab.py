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
    subgraph
)
from surfiamviz.webutils.utils import _set_attributes, _write_graph_to_file

repo_root = Path(os.path.realpath(__file__)).parent.parent.parent

def _subgraph(graph_config):
    st.header("Explore subgraphs")
    sub_form = st.form(key="Select subgraph")
    sub_col1, sub_col2 = sub_form.columns([2, 2])
    sel_edges = sub_col2.multiselect("Select Edges", graph_config["edge_colors"].keys())
    sel_nodes = sub_col1.multiselect("Select Nodes", graph_config["node_types"].keys())
    submit_subgraph = sub_form.form_submit_button("Render")
    return submit_subgraph, sel_edges, sel_nodes


def examples():
    """Examples tab."""
    st.title("SRAM example graphs")
    example_file = repo_root / "example_graphs/sram_examples.toml"
    if not example_file.is_file():
        st.write("Please make sure you downloaded the examples to example_graphs/sram_examples.toml.")
    example_graphs = import_example_graph(example_file)
    form = st.form(key="examples")
    option = form.selectbox(
        "Choose a graph:",
        example_graphs.keys(),
        index=None,
    )
    plotting_option = form.selectbox("Choose the plotting type:", ["bipartite", "greedy    ", "louvain"])
    form.form_submit_button("**Render**", icon=":material/thumb_up:")
    config_file = repo_root / "configs/sram_config.toml"
    if not config_file.is_file():
        st.write("Please make sure you downloaded the config file to configs/sram_config.toml.")
    graph_config = read_graph_config(config_file)
    if option:
        # plot example graph
        ex_graph = nx.MultiDiGraph()
        add_graph_edges_from_config(ex_graph, example_graphs, option)
        _set_attributes(ex_graph, graph_config)
        infer_coll_app_edges(ex_graph, True)
        color_edges(ex_graph, graph_config)
        if plotting_option:
            _write_graph_to_file(ex_graph, filename=repo_root / "gravis_html/example.html", plot_type=plotting_option)
        else:
            _write_graph_to_file(ex_graph, filename=repo_root / "gravis_html/example.html")
        with open(repo_root / "gravis_html/example.html", "r", encoding="utf-8") as htmlfile:
            components.html(htmlfile.read(), height=435)
        st.markdown(example_graphs[option]["explanation"])

        # option to create subgraphs
        submit_subgraph, sel_edges, sel_nodes = _subgraph(graph_config)
        if submit_subgraph:
            try:
                sg = subgraph(ex_graph, sel_edges, sel_nodes)
                _write_graph_to_file(sg, repo_root / "gravis_html/example_subgraph.html")
                with open(repo_root / "gravis_html/example_subgraph.html", "r", encoding="utf-8") as htmlfile:
                    components.html(htmlfile.read(), height=435)
            except ValueError:
                st.write(f"Graph does not contain nodes of type {sel_nodes}.")
