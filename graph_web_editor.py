"""A graph editor for the web browser."""

import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import tomllib

from surfiamviz.graph_from_config import (
    set_node_levels_from_config,
)
from surfiamviz.graph_from_sram_json import (
    get_nodes_from_dict,
    nodes_to_graph,
)
from surfiamviz.utils import (
    color_edges,
    color_nodes,
    render_editable_network,
    subgraph,
)


def _write_graph_to_file(g, filename="gravis_html/streamlit_graph.html", scaling="True"):
    if Path(filename).exists():
        Path(filename).unlink()
    render_editable_network(g, filename, scaling)


@st.cache_data
def _load_graph(g_config, s_dict):
    nodes = get_nodes_from_dict(s_dict)
    g = nodes_to_graph(nodes)
    set_node_levels_from_config(g, g_config)
    color_nodes(g, g_config)
    color_edges(g, g_config)
    return g


if "start" not in st.session_state:
    st.session_state.start = False


def _start_session():
    st.session_state.start = True


# layout
col1, col2, col3 = st.columns([1, 1, 1])

# init
sel_edges = []
sel_nodes = []

# Add a file uploader and downloader to the sidebar
upload_config = st.sidebar.file_uploader("Configuiration file", type=["toml"])
upload_sram_org = st.sidebar.file_uploader("SRAM organisation json", type=["json"])
start = st.sidebar.button("Start", on_click=_start_session)

if st.session_state.start:
    if upload_config is not None and upload_sram_org is not None:
        stringio = upload_config.getvalue().decode("utf-8")
        graph_config = tomllib.loads(str(stringio))
        # selection buttons
        stringio = upload_sram_org.getvalue().decode("utf-8")
        sram_dict = json.loads(stringio)

        graph = _load_graph(graph_config, sram_dict)
        _write_graph_to_file(graph)
        with open("gravis_html/streamlit_graph.html", "r", encoding="utf-8") as HtmlFile:
            components.html(HtmlFile.read(), height=435)

        with open("gravis_html/streamlit_graph.html", "rb") as buff:
            st.download_button(
                label="Download graph as HTML",
                data=buff,
                file_name="surfiam_network.html",
                mime="text/html",
                icon=":material/download:",
            )
        form = st.form(key="Select subgraph")
        with col1:
            sel_edges = form.multiselect("Select Edges", graph_config["edge_colors"].keys())
        with col2:
            sel_nodes = form.multiselect("Select Nodes", graph_config["node_types"].keys())
        with col3:
            submit_subgraph = form.form_submit_button("Render")

    if submit_subgraph:
        sg = subgraph(graph, sel_edges, sel_nodes)
        st.write(sg.nodes)
        _write_graph_to_file(sg, "gravis_html/subgraph.html", scaling=False)
        with open("gravis_html/subgraph.html", "r", encoding="utf-8") as HtmlFile:
            components.html(HtmlFile.read(), height=435)
