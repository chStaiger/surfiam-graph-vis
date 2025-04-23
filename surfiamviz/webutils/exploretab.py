"""Explore tab."""

import json
import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from surfiamviz.graph_from_sram_json import (
    get_nodes_from_dict,
    get_sram_org,
    get_sram_url,
    stats_dict,
)
from surfiamviz.utils import (
    read_graph_config,
    subgraph,
)
from surfiamviz.webutils.utils import _load_graph, _set_attributes, _write_graph_to_file

repo_root = Path(os.path.realpath(__file__)).parent.parent.parent


def _input():
    sram_form = st.form(key="sram_graph")
    config_path = repo_root / "configs"
    config_files = [x for x in config_path.glob("**/*") if x.is_file() and x.suffix == ".toml"]
    config_option = sram_form.selectbox("Choose a graph configuration:", config_files)
    sram_form.write("Provide API token:")
    col1, col2 = sram_form.columns([2, 2])
    api_key = col1.text_input("SRAM API key", type="password")
    sram_instance = col2.selectbox("SRAM instance", ("acc", "sram", "test"))
    sram_form.write("Or provide an exported SRAM file (json):")
    upload_sram_org = col1.file_uploader("SRAM organisation json", type=["json"])
    plotting_option = sram_form.selectbox("Choose the plotting type:", ["bipartite", "greedy", "louvain"])
    sram_form.form_submit_button("Render")
    return config_option, api_key, sram_instance, upload_sram_org, plotting_option


def _stats(sram_dict):
    st.header("Statistics of the Organisation")
    org_stats = stats_dict(get_nodes_from_dict(sram_dict))
    st.write(json.loads(org_stats))


def _subgraph(graph_config):
    st.header("Explore subgraphs")
    sub_form = st.form(key="Select subgraph")
    sub_col1, sub_col2 = sub_form.columns([2, 2])
    sel_edges = sub_col2.multiselect("Select Edges", graph_config["edge_colors"].keys())
    sel_nodes = sub_col1.multiselect("Select Nodes", graph_config["node_types"].keys())
    submit_subgraph = sub_form.form_submit_button("Render")
    return submit_subgraph, sel_edges, sel_nodes


def explore():
    """Load sram graphs and explore tab."""
    sram_dict = None
    st.title("Explore your own SRAM organisation.")
    config_option, api_key, sram_instance, upload_sram_org, plot = _input()
    if config_option:
        graph_config = read_graph_config(Path(config_option))
    else:
        st.write(f"Please create a config file in {repo_root / 'configs'}.")
    if api_key and sram_instance:
        server_url = get_sram_url(sram_instance)
        sram_dict = get_sram_org(api_key, server=server_url)
    elif upload_sram_org:
        stringio = upload_sram_org.getvalue().decode("utf-8")
        sram_dict = json.loads(stringio)
    else:
        st.write("Please provide information.")

    if sram_dict:
        sram_graph = _load_graph(sram_dict)
        _set_attributes(sram_graph, graph_config)
        _write_graph_to_file(sram_graph, filename=repo_root / "gravis_html/streamlit_graph.html", plot_type=plot)
        with open(repo_root / "gravis_html/streamlit_graph.html", "r", encoding="utf-8") as htmlfile:
            components.html(htmlfile.read(), height=435)

        submit_subgraph, sel_edges, sel_nodes = _subgraph(graph_config)

        if submit_subgraph:
            try:
                sg = subgraph(sram_graph, sel_edges, sel_nodes)
                _write_graph_to_file(sg, repo_root / "gravis_html/subgraph.html")
                with open(repo_root / "gravis_html/subgraph.html", "r", encoding="utf-8") as htmlfile:
                    components.html(htmlfile.read(), height=435)
            except ValueError:
                st.write(f"Graph does not contain nodes of type {sel_nodes}.")

        _stats(sram_dict)
