#!/usr/bin/env python3
"""Draw the plain sram graph."""

import argparse
import json
import pprint
import sys
from pathlib import Path

import networkx as nx
import requests

from surfiamviz.graph_from_config import (
    add_graph_edges_from_config,
    set_node_levels_from_config,
    set_node_type,
)
from surfiamviz.graph_from_sram_json import (
    get_nodes_from_dict,
    get_sram_org,
    get_sram_url,
    nodes_to_graph,
    read_json,
    stats_dict,
)
from surfiamviz.utils import (
    color_edges,
    color_nodes,
    read_graph_config,
    render_editable_network,
)

try:  # Python < 3.10 (backport)
    from importlib_metadata import version  # type: ignore
except ImportError:
    from importlib.metadata import version  # type: ignore [assignment]

MAIN_HELP_MESSAGE = f"""
SRAM graph visualisation version {version("surfiamviz")}

Usage: surfiamviz [subcommand] [options]

Available subcommands:
    organisation
        Generate the graph representation of the export to json of an SRAM organisation.
    graph
        Generate the graph representation from a section in the configuration file.
    stats
        Retrieve statistics from the export to json of an SRAM organisation.
    download
        Retrieve SRAM organisation json from SRAM.
    list
        List all available graphs from the configuration file.

Example usage:

    surfiamviz list -c configs/sram_config.toml
    surfiamviz graph -o test.html -c configs/sram_config.toml -g plain_graph -v

    surfiamviz organisation -i data/sram_test_org.json -o test.html -c configs/sram_config.toml
    surfiamviz organisation -o test.html -c configs/sram_config.toml --token TOKEN --server https://<server>

    surfiamviz stats -i data/sram_test_org.json
    surfiamviz stats --token TOKEN --server https://<server>s
    surfiamviz download --download <json_file> --server <server> --token <token>
"""


def main() -> None:
    """CLI with different entrypoints."""
    subcommand = "--help" if len(sys.argv) < 2 else sys.argv.pop(1)

    if subcommand in ["-h", "--help"]:
        print(MAIN_HELP_MESSAGE)
    elif subcommand in ["-v", "--version"]:
        print(f"surfiamviz version {version('surfiamviz')}")

    # find the subcommand in this module and run it!
    elif subcommand == "organisation":
        render_sram_graph()
    elif subcommand == "graph":
        render_graph_from_config()
    elif subcommand == "stats":
        get_stats_from_json()
    elif subcommand == "download":
        download_sram_org_json()
    elif subcommand == "list":
        list_config_graphs()
    else:
        print(f"Invalid subcommand ({subcommand}). For help see surfiamviz --help")
        sys.exit(1)


def render_sram_graph():
    """Render graph from the json export of an sram organisation."""
    parser = argparse.ArgumentParser(
        prog="surfiamviz organisation",
        description="Render the graph of an SRAM organisation from a json export file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path and name to store the generated html file.",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Configuration file defining node and edge types.",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "-v", "--verbose", help="Verbose output.", action="store_true", default=False
    )

    json_data = parser.add_argument_group(
        title="Render graph from a json export for the organisation."
    )
    json_data.add_argument(
        "-i",
        "--input",
        help="The path to the json file from an export of an SRAM organisation.",
        type=Path,
    )

    sram_connection = parser.add_argument_group(
        title="Connect to SRAM server with server name and token and render graph."
    )
    sram_connection.add_argument(
        "--server", help="The name of the SRAM ionstance: test, acc or sram (production)", type=str
    )
    sram_connection.add_argument(
        "--token",
        help="API token to the SRAM server.",
        type=str,
    )

    args = parser.parse_args()

    graph_config = _parse_config(args)
    if args.verbose:
        pprint.pprint(graph_config)

    sram_dict = _parse_input_or_token(args)
    if sram_dict is None:
        sys.exit(1)
    _parse_output(args)

    nodes = get_nodes_from_dict(sram_dict)
    graph = nodes_to_graph(nodes)
    set_node_levels_from_config(graph, graph_config)
    color_nodes(graph, graph_config)
    color_edges(graph, graph_config)
    render_editable_network(graph, args.output.absolute(), args.verbose)


def list_config_graphs():
    """List all sections in the config file that define graphs."""
    parser = argparse.ArgumentParser(
        prog="surfiamviz list",
        description="List the names of the graph sections from the configuration file.",
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Configuration file defining node, edge types and the graph(s).",
        type=Path,
        required=True,
    )
    args = parser.parse_args()

    graph_config = _parse_config(args)
    preset_sections = ["node_colors", "node_types", "edge_colors"]
    print("Availabel graphs:")
    print("\n".join([s for s in graph_config if s not in preset_sections]))


def render_graph_from_config():
    """Render a graph section from the configuration file."""
    parser = argparse.ArgumentParser(
        prog="surfiamviz graph", description="Render a graph section from the configuration file."
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Path and name to store the generated html file.",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Configuration file defining node, edge types and the graph(s).",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "-g",
        "--graph",
        help="the name of the section in the config file which defines the edges of the graph.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-v", "--verbose", help="Verbose output.", action="store_true", default=False
    )

    args = parser.parse_args()

    graph_config = _parse_config(args)
    if args.verbose:
        print("Configuration:")
        pprint.pprint(graph_config)

    if args.graph not in graph_config:
        print(f"Graph {args.graph} not defined in {args.config.absolute()}. Exit.")
        sys.exit(234)
    if args.verbose:
        print(f"Rendering {args.graph}")
        pprint.pprint(graph_config[args.graph])

    _parse_output(args)

    graph = nx.MultiDiGraph()
    add_graph_edges_from_config(graph, graph_config, args.graph)
    set_node_type(graph, graph_config)
    set_node_levels_from_config(graph, graph_config)
    color_nodes(graph, graph_config)
    color_edges(graph, graph_config)
    render_editable_network(graph, args.output.absolute(), args.verbose)


def get_stats_from_json():
    """Get statistics of an SRAM organisation."""
    parser = argparse.ArgumentParser(
        prog="surfiamviz stats", description="Retrieve statistics from SRAM json file."
    )

    json_data = parser.add_argument_group(
        title="Get statistics from a json export file for the organisation."
    )
    json_data.add_argument(
        "-i",
        "--input",
        help="The path to the json file from an export of an SRAM organisation.",
        type=Path,
    )

    sram_connection = parser.add_argument_group(
        title="Connect to SRAM server with server name and token and get statistcs."
    )
    sram_connection.add_argument(
        "--server", help="The name of the SRAM ionstance: test, acc or sram (production)", type=str
    )
    sram_connection.add_argument(
        "--token",
        help="API token to the SRAM server.",
        type=str,
    )

    args = parser.parse_args()

    sram_dict = _parse_input_or_token(args)
    if sram_dict is None:
        sys.exit(1)
    nodes = get_nodes_from_dict(sram_dict)
    print(stats_dict(nodes))


def download_sram_org_json():
    """Save the sram organisation json."""
    parser = argparse.ArgumentParser(
        prog="surfiamviz download", description="Download the SRAM organisation json."
    )

    parser.add_argument(
        "--server",
        help="The SRAM server, default: https://acc.sram.surf.nl",
        type=str,
        default="https://acc.sram.surf.nl",
    )

    parser.add_argument(
        "--token",
        help="API token to the SRAM server.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--file", help="The path and filename to save the json file.", type=Path, required=True
    )

    args = parser.parse_args()
    if not args.file.parent.is_dir():
        print(f"Cannot save json: {args.file.parent} does not exist.")
        sys.exit(1)
    try:
        org = get_sram_org(token=args.token, server=args.server)
    except requests.HTTPError as err:
        print(repr(err))
        sys.exit(1)

    with open(args.file, "w", encoding="utf-8") as fp:
        json.dump(org, fp)


def _parse_config(args: argparse.Namespace) -> dict:
    if args.config.is_file():
        try:
            graph_config = read_graph_config(args.config.absolute())
            return graph_config
        except Exception as error:
            print(f"Cannot read in {args.config}: {repr(error)}.")
            sys.exit(234)
    else:
        print(f"Config {args.config.absolute()} is directory or does not exist. Exit.")
        sys.exit(234)


def _parse_output(args: argparse.Namespace):
    if args.output.is_dir():
        print(f"Output {args.output} is a directory, cannot export graph.")
        sys.exit(234)
    elif args.output.is_file():
        confirm = input(f"Overwrite {args.output.absolute()} [Yes(ENTER)/No(Any key)]?")
        if confirm != "":
            sys.exit(234)
    else:
        print(f"Saving graph as {args.output.absolute()}.")


def _parse_input_or_token(args: argparse.Namespace) -> dict:
    if args.input and args.token:
        print("ERROR SRAM data: Please provide only an input file --input or")
        print("the information to fetch the organisation data from SRAM --server and --token.")
        return None
    if not args.input and not args.token:
        print("ERROR SRAM data: No data about organisation found.")
        print("You need to set either --input or --server and --token.")
        return None

    if args.input:
        if args.input.is_file():
            try:
                sram_dict = read_json(args.input)
                return sram_dict
            except Exception as error:
                print(f"Cannot read in {args.input}: {repr(error)}.")
                return None
        else:
            print(f"Input {args.input} is not a file or does not exist. Exit.")
            return None

    if args.token:
        if not args.server:
            print("ERROR SRAM server: no server name given (test, acc or sram).")
            return None
        server = get_sram_url(args.server)
        if server:
            try:
                sram_dict = get_sram_org(token=args.token, server=server)
                return sram_dict
            except requests.HTTPError as err:
                print(repr(err))
                return None
        else:
            print(f"Server {args.server} not known. Please choose from test, acc or sram.")
            return None
    return None
