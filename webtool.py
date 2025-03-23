import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
import json

from pathlib import Path
from surfiamviz.graph_from_config import (
    import_example_graph,
    add_graph_edges_from_config,
    set_node_type,
    set_node_levels_from_config,
)
from surfiamviz.utils import (
    read_graph_config,
    color_nodes,
    color_edges,
    infer_coll_app_edges,
    render_editable_network,
    subgraph,
)
from surfiamviz.graph_from_sram_json import (
    get_sram_url,
    get_sram_org,
    get_nodes_from_dict,
    nodes_to_graph,
    get_nodes_from_dict,
    stats_dict,
)


def _load_graph(g_config, s_dict):
    nodes = get_nodes_from_dict(s_dict)
    g = nodes_to_graph(nodes)
    return g

def _set_attributes(g, g_config):
    set_node_levels_from_config(g, g_config)
    set_node_type(g, g_config)
    color_nodes(g, g_config)
    color_edges(g, g_config)

def _write_graph_to_file(g, filename="gravis_html/streamlit_graph.html", scaling=True):
    if Path(filename).exists():
        Path(filename).unlink()
    render_editable_network(g, filename, scaling)


def welcome():
    st.title("Welcome to SURF's Idenity and Access management tools.")
    st.markdown('''
                This app aims to help you to understand SURF's IAM tools.
                We offer:
                    - Some example graphs which show the different roles and concepts SRAM implements and it shows the complexity and effects of actions.
                    - To visualise explore your own SRAM graph for your organisation.
                    - To create your own SRAM graph.
                ''')
    with open("all_nodes.html", "r", encoding="utf-8") as HtmlFile:
        components.html(HtmlFile.read(), height=435)


def examples():
    st.title("SRAM example graphs")
    example_file = Path("example_graphs/sram_examples.toml")
    if not example_file.is_file():
        st.write("Please make sure you downloaded the examples to example_graphs/sram_examples.toml.")
    example_graphs = import_example_graph(example_file)
    option = st.selectbox(
    "Choose a graph:",
    example_graphs.keys(),
    index=None,
    )
    config_file = Path("configs/sram_config.toml")
    if not config_file.is_file():
        st.write("Please make sure you downloaded the config file to configs/sram_config.toml.")
    graph_config = read_graph_config(config_file)
    if option:
        ex_graph = nx.MultiDiGraph()
        add_graph_edges_from_config(ex_graph, example_graphs, option)
        _set_attributes(ex_graph, graph_config)
        infer_coll_app_edges(ex_graph, True)
        color_edges(ex_graph, graph_config)
        _write_graph_to_file(ex_graph, filename="gravis_html/example.html", scaling=True)
        with open("gravis_html/example.html", "r", encoding="utf-8") as HtmlFile:
            components.html(HtmlFile.read(), height=435)
        st.write(example_graphs[option]["explanation"])


def explore():
    sram_dict = None
    st.title("Explore your own SRAM organisation.")
    sram_form = st.form(key="sram_graph")
    config_files = [x for x in Path("configs").glob('**/*') if x.is_file() and x.suffix == '.toml']
    config_option = sram_form.selectbox("Choose a graph configuration:", config_files)
    sram_form.write("Provide an exported SRAM file of your organisation or an API token:")
    col1, col2, col3, col4 = sram_form.columns([5, 1, 2, 2])
    upload_sram_org = col1.file_uploader("SRAM organisation json", type=["json"])
    col2.write("or")
    api_key = col3.text_input("SRAM API key", type="password")
    sram_instance = col4.selectbox("SRAM instance", ("acc", "sram", "test"))
    render_sram_graph = sram_form.form_submit_button("Render")

    graph_config = read_graph_config(Path(config_option))
    if api_key and sram_instance:
        server_url = get_sram_url(sram_instance)
        sram_dict = get_sram_org(api_key, server = server_url)
    elif upload_sram_org:
        stringio = upload_sram_org.getvalue().decode("utf-8")
        sram_dict = json.loads(stringio)
    else:
        st.write("Please provide information.")

    if sram_dict:
        sram_graph = _load_graph(graph_config, sram_dict)
        _set_attributes(sram_graph, graph_config)
        _write_graph_to_file(sram_graph)
        with open("gravis_html/streamlit_graph.html", "r", encoding="utf-8") as HtmlFile:
            components.html(HtmlFile.read(), height=435)

        st.header("Explore subgraphs")
        sub_form = st.form(key="Select subgraph")
        sub_col1, sub_col2 = sub_form.columns([2, 2])
        sel_edges = sub_col2.multiselect("Select Edges", graph_config["edge_colors"].keys())
        sel_nodes = sub_col1.multiselect("Select Nodes", graph_config["node_types"].keys())
        submit_subgraph = sub_form.form_submit_button("Render")

        if submit_subgraph:
            sg = subgraph(sram_graph, sel_edges, sel_nodes)
            _write_graph_to_file(sg, "gravis_html/subgraph.html", scaling=False)
            with open("gravis_html/subgraph.html", "r", encoding="utf-8") as HtmlFile:
                components.html(HtmlFile.read(), height=435)

        st.header("Statistics of the Organisation")
        org_stats = stats_dict(get_nodes_from_dict(sram_dict))
        print(type(org_stats))
        st.write(json.loads(org_stats))

def create():
    st.title("Create your own SRAM organisation graph.")

pg = st.navigation([welcome, examples, explore, create])
pg.run()

